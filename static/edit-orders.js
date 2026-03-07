document.addEventListener("DOMContentLoaded", function () {

    loadUpcomingOrders();
    loadCompletedOrders();
    initTabs();

});


/* --------------------------
LOAD UPCOMING ORDERS
--------------------------*/

function loadUpcomingOrders(){

    const table = document.getElementById("upcoming-orders-body");
    if(!table) return;

    fetch("/upcoming-orders")

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

                        <button class="btn-delete"
                        onclick="deleteOrder('${order.orderid}')">

                        <i class="fa fa-trash"></i>
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

    fetch("/completed-orders")

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

                    <button class="btn-delete"
                    onclick="deleteOrder('${order.orderid}')">

                    <i class="fa fa-trash"></i>
                    </button>

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

    fetch("/delete-production-order",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body: JSON.stringify({
            orderid: orderid
        })

    })

    .then(res => res.json())

    .then(() => {

        loadUpcomingOrders();
        loadCompletedOrders();

    });

}


/* --------------------------
TAB SYSTEM
--------------------------*/

function initTabs(){

    const buttons = document.querySelectorAll(".tab-button");

    buttons.forEach(btn => {

        btn.addEventListener("click", () => {

            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const tab = btn.dataset.tab;

            document.getElementById("upcoming-orders-table").style.display =
                tab === "upcoming" ? "table" : "none";

            document.getElementById("completed-orders-table").style.display =
                tab === "completed" ? "table" : "none";

        });

    });

}