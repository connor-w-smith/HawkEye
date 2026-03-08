document.addEventListener("DOMContentLoaded", function () {

    // ----- Globals -----
    let currentEditingOrder = null;
    let currentEditingFinishedGood = null;
    let currentEditingType = null;

    // ----- DOM Elements -----
    const completedModal = document.getElementById("add-completed-order-modal");
    const completedBtn = document.getElementById("add-completed-btn");
    const productionBtn = document.querySelector(".add-order-btn");
    const buttons = document.querySelectorAll(".tab-button");
    const editForm = document.getElementById("edit-order-form");
    const editModal = document.getElementById("edit-order-modal");
    const editModalMessage = document.getElementById("edit-order-modal-message");

    // ----- Tab System -----
    function showTab(tab) {
        document.getElementById("upcoming-orders-table").style.display = tab === "upcoming" ? "table" : "none";
        document.getElementById("completed-orders-table").style.display = tab === "completed" ? "table" : "none";
        if(productionBtn) productionBtn.style.display = tab === "upcoming" ? "inline-block" : "none";
        //if(completedBtn) completedBtn.style.display = tab === "completed" ? "inline-block" : "none";
        buttons.forEach(b => b.classList.remove("active"));
        buttons.forEach(b => { if(b.dataset.tab === tab) b.classList.add("active"); });
    }
    showTab("upcoming");
    buttons.forEach(btn => btn.addEventListener("click", () => showTab(btn.dataset.tab)));

    // ----- Load Tables -----
    loadUpcomingOrders();
    loadCompletedOrders();

    // -----------------------------
    // EDIT ORDER MODAL FUNCTIONS
    // -----------------------------
    window.openEditOrderModal = function(type, orderid, quantity, sensor, finishedgoodid){
        currentEditingType = type;
        currentEditingOrder = orderid;
        currentEditingFinishedGood = finishedgoodid || null;
    
        const sensorGroup = document.getElementById("edit-order-sensor").closest(".form-group"); // entire form group
        const sensorField = document.getElementById("edit-order-sensor");
        const startField = document.getElementById("edit-order-start-time");
        const endField = document.getElementById("edit-order-end-time");
        document.getElementById("edit-order-quantity").value = quantity;
    
        if(type === "upcoming"){
            loadSensorOptions();
            if(sensorGroup) sensorGroup.style.display = "block";
            sensorField.disabled = false;
            sensorField.value = sensor || "";
            if(startField){ startField.style.display = "none"; startField.disabled = true; }
            if(endField){ endField.style.display = "none"; endField.disabled = true; }
        }
    
        if(type === "completed"){
            if(sensorGroup) sensorGroup.style.display = "none"; // hide sensor completely
            sensorField.disabled = true;
            if(startField){ startField.style.display = "block"; startField.disabled = false; }
            if(endField){ endField.style.display = "block"; endField.disabled = false; }
        }
    
        if(editModalMessage){
            editModalMessage.textContent = "";
            editModalMessage.style.color = "";
        }
    
        editModal.style.display = "block";
    }

    const closeEditBtn = editModal ? editModal.querySelector(".close") : null;
    if(closeEditBtn) closeEditBtn.addEventListener("click", ()=>{ editModal.style.display = "none"; });
    window.addEventListener("click", (event)=>{ if(event.target === editModal){ editModal.style.display = "none"; } });

    // ----- Edit Form Submit -----
    if(editForm){
        editForm.addEventListener("submit", async function(e){
            e.preventDefault();

            if(!currentEditingOrder){
                alert("No order selected to edit.");
                return;
            }

            const quantity = parseInt(document.getElementById("edit-order-quantity").value);
            const sensor = document.getElementById("edit-order-sensor").value;

            let endpoint = "";
            let payload = {};

            if(currentEditingType === "upcoming"){
                endpoint = "/orders/update-production-order";
                payload = {
                    orderid: currentEditingOrder,
                    finishedgoodid: currentEditingFinishedGood,
                    target_quantity: quantity,
                    sensor_id: sensor || null
                };
            } else if(currentEditingType === "completed"){
                const startTime = document.getElementById("edit-order-start-time").value;
                const endTime = document.getElementById("edit-order-end-time").value;
                endpoint = "/orders/update-completed-order";
                payload = {
                    orderid: currentEditingOrder,
                    partsproduced: quantity,
                    start_time: startTime,
                    end_time: endTime
                };
            } else {
                alert("Unknown order type.");
                return;
            }

            try {
                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(payload)
                });

                let data = {};
                try { data = await response.json(); } catch(_) { data = {status:"error", message:"Invalid JSON from server"}; }

                if(response.ok && data.status === "success"){
                    if(editModalMessage){
                        editModalMessage.style.color = "green";
                        editModalMessage.textContent = "Order updated successfully!";
                    }
                    setTimeout(()=>{
                        editModal.style.display = "none";
                        loadUpcomingOrders();
                        loadCompletedOrders();
                    }, 800);
                } else {
                    if(editModalMessage){
                        editModalMessage.style.color = "red";
                        editModalMessage.textContent = data.message || JSON.stringify(data);
                        console.error("API error:", data);
                    }
                }

            } catch(err){
                console.error("Fetch error:", err);
                if(editModalMessage){
                    editModalMessage.style.color = "red";
                    editModalMessage.textContent = err.message;
                }
            }
        });
    }

    // -----------------------------
    // ADD ORDER MODAL FUNCTIONS
    // -----------------------------
    const addModal = document.getElementById("add-order-modal");
    const addForm = document.getElementById("add-order-form");
    const addCloseBtn = addModal ? addModal.querySelector(".close") : null;

    if(productionBtn) productionBtn.addEventListener("click", openAddOrderModal);
    if(addCloseBtn) addCloseBtn.addEventListener("click", ()=>{ addModal.style.display = "none"; });
    window.addEventListener("click", (event)=>{ if(event.target === addModal) addModal.style.display = "none"; });

    if(addForm){
        addForm.addEventListener("submit", async (e)=>{
            e.preventDefault();

            const finishedgoodid = document.getElementById("add-order-finished-good").value;
            const targetQuantity = parseInt(document.getElementById("add-order-quantity").value);
            const sensorId = document.getElementById("add-order-sensor").value || null;
            const messageBox = document.getElementById("add-order-modal-message");

            if(messageBox){
                messageBox.textContent = "Creating production order...";
                messageBox.style.color = "blue";
            }

            try {
                const response = await fetch("/orders/create-production-order", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ finishedgoodid, target_quantity: targetQuantity, sensor_id: sensorId })
                });

                let data = {};
                try { data = await response.json(); } catch(_) { data = {status:"error", message:"Invalid JSON from server"}; }

                if(response.ok && data.status === "success"){
                    if(messageBox){
                        messageBox.style.color = "green";
                        messageBox.textContent = `✓ Production Order Created! Order ID: ${data.orderid}`;
                    }
                    loadUpcomingOrders();
                    loadCompletedOrders();
                    setTimeout(()=>{ addModal.style.display = "none"; }, 1000);
                } else {
                    if(messageBox){
                        messageBox.style.color = "red";
                        messageBox.textContent = data.message || JSON.stringify(data);
                    }
                }
            } catch(err){
                console.error("Add order error:", err);
                if(messageBox){
                    messageBox.style.color = "red";
                    messageBox.textContent = err.message;
                }
            }
        });
    }

    // -----------------------------
    // UTILITY FUNCTIONS
    // -----------------------------
    function loadUpcomingOrders(){
        const table = document.getElementById("upcoming-orders-body");
        if(!table) return;
        fetch("/search/upcoming-orders")
            .then(res => res.json())
            .then(data => {
                table.innerHTML = "";
                data.forEach(order => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${order.orderid}</td>
                        <td>${order.finishedgoodname}</td>
                        <td>${order.target_quantity}</td>
                        <td>${order.sensor_id || "-"}</td>
                        <td>
                            <div class="actions-container">
                                <button class="btn-edit" onclick="openEditOrderModal(
                                    'upcoming',
                                    '${order.orderid}',
                                    '${order.target_quantity}',
                                    '${order.sensor_id || ""}',
                                    '${order.finishedgoodid}'
                                )"><i class="fa fa-edit"></i> Edit</button>
                                <button class="btn-delete" onclick="deleteOrder('${order.orderid}')"><i class="fa fa-trash"></i> Delete</button>
                            </div>
                        </td>`;
                    table.appendChild(row);
                });
            });
    }

    function loadCompletedOrders(){
        const table = document.getElementById("completed-orders-body");
        if(!table) return;
        fetch("/search/completed-orders")
            .then(res => res.json())
            .then(data => {
                table.innerHTML = "";
                data.forEach(order => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${order.orderid}</td>
                        <td>${order.finishedgoodname}</td>
                        <td>${order.partsproduced}</td>
                        <td>
                            <div class="actions-container">
                                <button class="btn-edit" onclick="openEditOrderModal(
                                    'completed',
                                    '${order.orderid}',
                                    '${order.partsproduced}',
                                    '${order.sensor_id || ""}',
                                    '${order.finishedgoodid}'
                                )"><i class="fa fa-edit"></i> Edit</button>
                                <button class="btn-delete" onclick="deleteOrder('${order.orderid}')"><i class="fa fa-trash"></i> Delete</button>
                            </div>
                        </td>`;
                    table.appendChild(row);
                });
            });
    }

    window.deleteOrder = function(orderid){
        if(!confirm("Delete this production order?")) return;
        fetch("/orders/delete-production-order", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({orderid})
        }).then(()=>{ loadUpcomingOrders(); loadCompletedOrders(); });
    }

    function loadSensorOptions(){
        const dropdown = document.getElementById("edit-order-sensor");
        if(!dropdown) return;
        dropdown.innerHTML = "";
        ["Sensor_A","Sensor_B"].forEach(sensor=>{
            const option = document.createElement("option");
            option.value = sensor;
            option.textContent = sensor;
            dropdown.appendChild(option);
        });
    }

    function openAddOrderModal(){
        if(!addModal) return;
        addModal.style.display = "block";

        // populate finished goods
        const finishedDropdown = document.getElementById("add-order-finished-good");
        finishedDropdown.innerHTML = "";
        fetch("/products/finished-goods?search=")
            .then(res=>res.json())
            .then(data=>{
                if(data.status==="success" && data.results){
                    data.results.forEach(item=>{
                        const opt = document.createElement("option");
                        opt.value = item.FinishedGoodID;
                        opt.textContent = item.FinishedGoodName;
                        finishedDropdown.appendChild(opt);
                    });
                }
            });

        // populate sensors
        const sensorDropdown = document.getElementById("add-order-sensor");
        sensorDropdown.innerHTML = "";
        ["Sensor_A","Sensor_B"].forEach(sensor=>{
            const option = document.createElement("option");
            option.value = sensor;
            option.textContent = sensor;
            sensorDropdown.appendChild(option);
        });

        const msg = document.getElementById("add-order-modal-message");
        if(msg){ msg.textContent = ""; msg.style.color = ""; }
    }
});