document.addEventListener("DOMContentLoaded", function () {

    // Load tables when page loads
    loadUpcomingOrders();
    loadCompletedOrders();
    initTabs();

    const editForm = document.getElementById("edit-order-form");
    const editModalMessage = document.getElementById("edit-order-modal-message");

    if(editForm){
        editForm.addEventListener("submit", async function(e){
            e.preventDefault();

            const quantity = document.getElementById("edit-order-quantity").value;
            const sensor = document.getElementById("edit-order-sensor").value;

            if(!currentEditingOrder || !currentEditingFinishedGood){
                alert("No order selected to edit.");
                return;
            }

            try{
                const response = await fetch("/orders/update-production-order", {
                    method:"POST",
                    headers:{"Content-Type":"application/json"},
                    body: JSON.stringify({
                        orderid: currentEditingOrder,
                        finishedgoodid: currentEditingFinishedGood,
                        target_quantity: parseInt(quantity),
                        sensor_id: sensor || null
                    })
            
                });

                const data = await response.json();

                if(response.ok && data.status === "success"){
                    if(editModalMessage){
                        editModalMessage.style.color = "green";
                        editModalMessage.textContent = "Order updated successfully!";
                    }

                    setTimeout(()=>{
                        document.getElementById("edit-order-modal").style.display = "none";
                        loadUpcomingOrders();
                        loadCompletedOrders();
                    }, 800);

                }else{
                    if(editModalMessage){
                        editModalMessage.style.color = "red";
                        editModalMessage.textContent = data.message || JSON.stringify(data);
                        console.log("API error:", data);
                    }
                }

            }catch(err){
                console.error("Update error:", err);
                if(editModalMessage){
                    editModalMessage.style.color = "red";
                    editModalMessage.textContent = err.message;
                }
            }

        });
    }

    const editModal = document.getElementById("edit-order-modal");
    const closeBtn = editModal ? editModal.querySelector(".close") : null;

    if(closeBtn){
        closeBtn.addEventListener("click",()=>{ editModal.style.display = "none"; });
    }

    window.addEventListener("click",(event)=>{
        if(event.target === editModal){ editModal.style.display = "none"; }
    });

});

let currentEditingOrder = null;
let currentEditingFinishedGood = null;

/* --------------------------
LOAD UPCOMING ORDERS
--------------------------*/
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
                            '${order.orderid}',
                            '${order.target_quantity}',
                            '${order.sensor_id || ""}',
                            '${order.finishedgoodid}'   // now defined
                        )">
                        <i class="fa fa-edit"></i> Edit
                    </button>

                        <button class="btn-delete" onclick="deleteOrder('${order.orderid}')">
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
            table.appendChild(row);
        });
    });
}

/* --------------------------
LOAD COMPLETED ORDERS
--------------------------*/
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
                <td>${order.target_quantity}</td>
                <td>${order.partsproduced}</td>
                <td>
                    <div class="actions-container">
                        <button class="btn-edit" onclick="openEditOrderModal(
                            '${order.orderid}',
                            '${order.target_quantity}',
                            '${order.sensor_id || ""}',
                            '${order.finishedgoodid}'
                        )"><i class="fa fa-edit"></i> Edit</button>

                        <button class="btn-delete" onclick="deleteOrder('${order.orderid}')">
                            <i class="fa fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
            table.appendChild(row);
        });
    });
}

/* --------------------------
DELETE ORDER
--------------------------*/
function deleteOrder(orderid){
    if(!confirm("Delete this production order?")) return;

    fetch("/orders/delete-production-order", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ orderid })
    })
    .then(res => res.json())
    .then(()=>{
        loadUpcomingOrders();
        loadCompletedOrders();
    });
}

/* --------------------------
LOAD SENSOR OPTIONS
--------------------------*/
function loadSensorOptions(){
    const dropdown = document.getElementById("edit-order-sensor");
    if(!dropdown) return;

    dropdown.innerHTML = "";
    const sensors = ["Sensor_A","Sensor_B"];
    sensors.forEach(sensor=>{
        const option = document.createElement("option");
        option.value = sensor;
        option.textContent = sensor;
        dropdown.appendChild(option);
    });
}

/* --------------------------
OPEN EDIT MODAL
--------------------------*/
window.openEditOrderModal = function(orderid, quantity, sensor, finishedgoodid){
    currentEditingOrder = orderid;
    currentEditingFinishedGood = finishedgoodid || null; // <- fallback to null
    loadSensorOptions();

    document.getElementById("edit-order-quantity").value = quantity;
    document.getElementById("edit-order-sensor").value = sensor || "";

    const message = document.getElementById("edit-order-modal-message");
    if(message){ message.textContent = ""; message.style.color = ""; }

    document.getElementById("edit-order-modal").style.display = "block";
}

/* --------------------------
TAB SYSTEM
--------------------------*/
function initTabs(){
    const buttons = document.querySelectorAll(".tab-button");
    buttons.forEach(btn=>{
        btn.addEventListener("click",()=>{
            buttons.forEach(b=>b.classList.remove("active"));
            btn.classList.add("active");
            const tab = btn.dataset.tab;
            document.getElementById("upcoming-orders-table").style.display = tab==="upcoming" ? "table" : "none";
            document.getElementById("completed-orders-table").style.display = tab==="completed" ? "table" : "none";
        });
    });
}