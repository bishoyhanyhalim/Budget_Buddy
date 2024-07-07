console.log("hello world");
const x = document.querySelector("#x");
const y = document.querySelector("#y");
const z = document.querySelector("#z");
const dateInput = document.querySelector("#dateInput");
const timeInput = document.querySelector("#timeInput");
const form = document.querySelector("#handle");
const result = document.querySelector("#result");
const update = document.querySelector("#update");
const updateEdit = document.querySelector("#updateEdit");
let expense = document.getElementById("expense-section");
const add = document.getElementById("add");
let expense_update = document.getElementById("expense-sectio");
const row = document.getElementById("newrow");
const dateInput_update = document.querySelector("#dateInput-update");
const timeInput_update = document.querySelector("#timeInput-update");
var dataList = [];

const updateAddToData = document.getElementById("update-row-btn");
const totalBudget = document.getElementById("total-budget");
const money_left = document.getElementById("remadnder");
const home_title = document.getElementById("home-title");
const update_title = document.getElementById("update-title");
const update_form = document.getElementById("update_form");
const add_form = document.getElementById("add-form");
const x_update = document.getElementById("x-update");
const y_update = document.getElementById("y-update");
var remainder_on_load = 0;
if (JSON.parse(localStorage.getItem("data"))) {
  dataList = JSON.parse(localStorage.getItem("data"));
}
console.log(dataList);
function loadData() {
  fetch(`/loadcontent`)
    .then((response) => response.json())

    .then((data) => {
      // if (data.message === "please login"){
      //     swl("login","login", "success")
      // }
      //   money_left.innerHTML= `<h2> ${data.Remainder}</h2>`
      //
      // else{
      console.log("data at load:", data);
      localStorage.setItem(`data`, JSON.stringify(data));
      dataList = JSON.parse(localStorage.getItem("data"));
      //  let filteredData = allData.filter(item=> item.Paid !== 0)
      //   console.log(filteredData)
      dataList.map((data) => {
        const dateObject = new Date(data.Date_created);
        // Format the Date object to display only the date
        const dateString = dateObject.toLocaleDateString();
        //  const timeObject = new Date(data.Time_created);
        // Format the Date object to display only the time
        //const timeString = timeObject.toTimeString();
        row.innerHTML += `
            <tr class="text-center" id="row-${data.Id}">
                           <th scope="row"></th>
                           <td id="paid-${data.Id}"> ${data.Total_added}</td>
                           <td id="paid-${data.Id}"> ${data.Paid}</td>
                           
                           <td> ${data.Section}</td>
                                   <td> ${dateString}</td>
                                    <td> ${data.Time_created}</td>
                           <td> <button class="btn btn-danger btndelete" id="btndelete" onClick="delete_row(${data.Id})"><i class="fa fa-trash"></i> Delete</button>
                           </td>
                           <td><button class="btn btn-primary" id="uppbtn" onclick="update_row(${data.Id})">
                               update
                              </button></td>
                              
                           </tr>
                           `;
        updateIndex();
        clear();
      });
      //  }

      console.log(this);
    });
}
loadData();
//this event listener prevent refresh and you can get input value with id.value
// add and calculate first operation
let originalInnerHTML; // Store the original innerHTML of money_left
/*setInterval(async function(){
  /*  let allData = JSON.parse(localStorage.getItem("data"));
    let filteredData = allData.filter(item=> item.Paid === 0);
    if (allData.length === filteredData.length )
        {reset.classList.replace("d-none","d-block");}
    else{
        reset.classList.replace("d-block", "d-none");
    }*/

/*  try {
        let remainder = await getRemainder(); // Await the promise to resolve
        console.log(remainder); // Log the remainder value
        money_left.innerHTML = ` Money left in wallet: <h2>${remainder}</h2>`; // Update the innerHTML with the remainder
    } catch (error) {
        console.error('Failed to get remainder:', error);
    }
}, 5000)*/
money_left.addEventListener("click", async function (event) {
  event.preventDefault();

  try {
    let remainder = await getRemainder(); // Await the promise to resolve
    console.log(remainder); // Log the remainder value
    money_left.innerHTML = `<h2>${remainder}</h2>`; // Update the innerHTML with the remainder
  } catch (error) {
    console.error("Failed to get remainder:", error);
  }
});

async function getRemainder() {
  let url = "/remainder";

  let request_options = {
    method: "GET",
    headers: {
      "content-type": "application/json",
    },
  };
  let response = await fetch(url, request_options);
  let data = await response.json();

  console.log(data);
  // money_left.innerHTML= `<h2>${data}</h2>`
  // originalInnerHTML = money_left.innerHTML;
  return data.remainder;
}
form.addEventListener("submit", async (event) => {
  let url = "/add";
  event.preventDefault();
  let x_value;
  if (!x.value) {
    x_value = parseInt(0);
  } else {
    x_value = parseInt(x.value);
  }
  let y_value;
  if (!y.value) {
    y_value = parseInt(0);
  } else {
    y_value = parseInt(y.value);
  }
  // expense = expence.value;
  remainder_on_load = await getRemainder();
  console.log("x_value", x_value, "y_value", y_value);
  if (x_value < y_value && remainder_on_load < y_value) {
    // alert()
    swal("0!", "you have no money", "success");
  } else {
    let request_options = {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        x: x_value,
        y: y_value,
        expense: expense.value,
        date: dateInput.value,
        time: timeInput.value,
      }),
    };
    fetch(url, request_options)
      .then((response) => {
        if (!response.ok) {
          // Check if the response indicates an error or redirection
          console.log(response);
          if (response.status === 401 || response.redirected) {
            // Redirect to login page
            window.location.href = "/login";
          } else {
            throw new Error("Network response was not ok");
          }
        }
        return response.json();
      })
      .then((data) => {
        dataList.push(data);
        localStorage.setItem("data", JSON.stringify(dataList));
        console.log("dataList after add:", dataList);
        if (data.message === "login please") {
          window.location.href = "/login";
        } else {
        /* else if(data.Paid === 0){
        return;
       }*/
          const dateObject = new Date(data.Date_created);

          // Format the Date object to display only the date
          const dateString = dateObject.toLocaleDateString();
          //  const timeObject = new Date(data.Time_created);

          // Format the Date object to display only the time
          //  const timeString = timeObject.toTimeString();
          // money_left.innerHTML = `<h2> ${data.Remainder}</h2>`

          row.innerHTML += `
        <tr class="text-center" id="row-${data.Id}">
                       <th scope="row"></th>
                        <td id="paid-${data.Id}"> ${data.Total_added}</td>
                       <td id="paid-${data.Id}"> ${data.Paid}</td>
                      
                       <td> ${data.Section}</td>
                        <td> ${dateString}</td>
                        <td> ${data.Time_created}</td>
                       <td> <button class="btn btn-danger btndelete" id="btndelete" onClick="delete_row(${data.Id})"><i class="fa fa-trash"></i> Delete</button>
                       </td>
                       <td><button class="btn btn-primary" id="uppbtn" onclick="update_row(${data.Id})">
                           update
                          </button></td>
                       </tr>
                      
                       `;
          console.log(data);
          updateIndex();
          daleted_lastremainder_value = data.Remainder;
          clear(); //clear input fields after submit
          x.value = null;
          y.value = null;
          dateInput = null;
          timeInput = null;
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }
});
var today = new Date();
document.addEventListener("DOMContentLoaded", function () {
  // Get today's date in YYYY-MM-DD format

  var dd = String(today.getDate()).padStart(2, "0");
  var mm = String(today.getMonth() + 1).padStart(2, "0"); // January is 0!
  var yyyy = today.getFullYear();

  today = yyyy + "-" + mm + "-" + dd;

  // Find the input field and set its value to today's date
  document.getElementById("dateInput").value = today;
});

let row_index = 0;
let deleted_spent_value = 0;
let daleted_lastremainder_value = 0;
function delete_row(itemId) {
  console.log(itemId);
  let trrows = document.querySelectorAll("tbody tr");
  console.log(trrows);
  trrows.forEach((tr) => {
    if (tr.getAttribute("id").startsWith(`row-${itemId}`)) {
      deleted_spent_value = tr.children[2].textContent;
      row_index = tr.children[0].textContent;
    }
  });
  //letsUpdateDataBaseAfterDelete()

  fetch(`/ditems/${itemId}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);

      // Logic to remove the row from the UI
      if (data.message === "Item deleted successfully") {
        // Logic to remove the row from the UI

        letsDelete(itemId);
        updateIndex();
        console.log("row_index", row_index);
        dataList.splice(row_index - 1, 1);
        localStorage.setItem("data", JSON.stringify(dataList));
        console.log("dataList after delete:", dataList);
        //  money_left.innerHTML= `<h2> ${data.Remainder}</h2>`
      } else {
        console.error("Failed to delete item");
      }
    })
    .catch((error) => console.error("Error:", error));
}
/*
function letsUpdateDataBaseAfterDelete(){
    let URL='/upatingAfterDelete'
  
   x_value = parseInt(daleted_lastremainder_value);
   y_value = parseInt(deleted_spent_value);
  // expense = expence.value;
   let request_options={
    method:"POST",
    headers:{
        'content-type':'application/json',

    },
    body:JSON.stringify({x:x_value,y:y_value})
}
fetch(URL,request_options)
    .then(response=>{if (!response.ok) { // Check if the response indicates an error or redirection
        if (response.status === 401 || response.statusText === 'Unauthorized') {
            // Redirect to login page
            window.location.href = '/login';
        } else {
            throw new Error('Network response was not ok');
        }
    }
    return response.json();
})
    .then((data)=>{
       
        console.log(data)
       
            row.innerHTML += `
            <h2> you budget is ${data.Remainder}</h2>
            `
          console.log(this)
   
          
    daleted_lastremainder_value = data.Remainder;
         
        
        
    })
    .catch((err)=>console.log(err))
} */

function updateIndex() {
  let trrows = document.querySelectorAll("tr");
  console.log(trrows);
  for (var i = 1; i < trrows.length; i++) {
    // Access the first <td> of each row
    var firstTd = trrows[i].children[0];
    console.log(firstTd);
    // Change the text content of the first <td>
    firstTd.textContent = i;
  }
}

function letsDelete(itemId) {
  let rowToDelete = document.querySelector(`#row-${itemId}`);
  console.log(rowToDelete);
  if (rowToDelete) {
    row.removeChild(rowToDelete);
  }
}

let indexUpdate;
let idForUpdate = 0;

const allRows = document.querySelectorAll("#row tr");

function update_row(row_id) {
  let trrows = document.querySelectorAll("tbody tr");
  trrows.forEach((tr) => {
    console.log(tr);
    if (tr.getAttribute("id").startsWith(`row-${row_id}`)) {
      indexUpdate = tr.children[0].textContent;
      //   x_update.value = tr.children[2].textContent
      //   y_update.value = tr.children[1].textContent

      console.log(indexUpdate);
    }
  });
  add_form.classList.replace("d-block", "d-none");
  update_form.classList.replace("d-none", "d-block");
  home_title.classList.replace("d-inline-block", "d-none");
  update_title.classList.replace("d-none", "d-inline-block");

  let updatedPay = document.querySelector(`#paid-${row_id}`);
  //let updatedTotal = document.querySelector(`#total-${row_id}`);
  /*dataList.filter((item)=>{ item.Id === row_id}){
    y_update.value = 
}*/
  let allData = JSON.parse(localStorage.getItem("data"));
  let filteredData = allData.filter((data) => data.Id === row_id);
  console.log("filteredData", filteredData);
  x_update.value = parseInt(filteredData[0].Total_added);
  y_update.value = parseInt(filteredData[0].Paid);
  dateInput_update.value = filteredData[0].Date_created;
  timeInput_update.value = filteredData[0].Time_created;
  console.log(dateInput_update.value);
  console.log(" x_update.value ", x_update.value);
  console.log(" y_update.value ", y_update.value);
  idForUpdate = row_id;
  console.log(idForUpdate);
}

update_form.addEventListener("submit", async (event) => {
  console.log("updating event", event);
  let itemId = idForUpdate;
  console.log("item id that will be updated", itemId);
  const URL = `/upitems/${itemId}`;
  event.preventDefault();
  let x_value;
  if (!x_update.value) {
    x_value = parseInt(0);
  } else {
    x_value = parseInt(x_update.value);
  }
  let y_value;
  if (!y_update.value) {
    y_value = parseInt(0);
  } else {
    y_value = parseInt(y_update.value);
  }
  // expense = expence.value;
  remainder_on_load = await getRemainder();
  console.log("remainder before update", remainder_on_load);
  if (x_value < y_value && remainder_on_load < y_value) {
    swal("$$$!", "You have No money", "danger");
  } else {
    let request_options = {
      method: "PUT",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        x: x_value,
        y: y_value,
        expense: expense_update.value,
        date: dateInput_update.value,
        time: timeInput_update.value,
      }),
    };
    fetch(URL, request_options)
      .then((response) => {
        if (response.message === "Record not found") {
          swal("$$$!", "something went wrong try again", "danger");
        } else {
          response.json();
        }
      })
      .then((data) => {
        console.log("data after update", data);

        //  handleUpdate(data);
        row.innerHTML = "";
        loadData();
        update_form.classList.replace("d-block", "d-none");
        add_form.classList.replace("d-none", "d-block");
        update_title.classList.replace("d-inline-block", "d-none");
        home_title.classList.replace("d-none", "d-inline-block");
        x_update.value = null;
        y_update.value = null;
        dateInput_update.value = null;
        timeInput_update.value = null;
      })

      .catch((err) => console.log(err));
  }
});

/*function handleUpdate(data){
    console.log("updated data",data)
     
    var rowIndex = parseInt(indexUpdate);
    if(data.Paid === 0){
        console.log("data.paid at update is:",data.Paid)
       letsDelete(rowIndex);
       updateIndex()
      return
      
    }
   // else{
         letsDelete(rowIndex);
        // Assuming 'data.Id' gives you the index where you want to insert the row
   console.log(rowIndex)
   var tr = document.createElement('tr');
   tr.setAttribute('id',"row-" + data.Id)
         var newRowHtml = `
        
            <th scope="row">${indexUpdate}</th>
             <td id="paid-${data.Id}">${data.Paid}</td>
            
            <td>${data.Section}</td>
           <td>${data.Date_updated}</td>
          <td><button class="btn btn-danger btndelete" id="btndelete" onClick="delete_row(${data.Id})"><i class="fa fa-trash"></i> Delete</button></td>
            <td><button class="btn btn-primary" id="uppbtn" onclick="update_row(${data.Id})">Update</button></td>
            
         `;

       
         tr.innerHTML = newRowHtml;
     
         // 4. Get the newly created row element
       
         console.log("newRow after update", tr)
   
        // console.log("newHTML after update",newRowHtml)
        // console.log("row.children[0] is :",row.children[0])
         //row.insertBefore(tr, row.children[0]);
         // 5. Check if the index is valid and there's a reference node to insert before
         console.log("length of the rows is: ",row.children.length)
       //  if (rowIndex >= 0 && rowIndex <= row.children.length) {
             // 6. Insert the new row before the reference node
             
             console.log("inside if",row.children[indexUpdate - 1])
             row.insertBefore(tr, row.children[indexUpdate -1]);
       //  } else {
            // console.error('Invalid index:', rowIndex);
       //  }
      // }
   
       
    update_form.classList.replace("d-block", "d-none");
    add_form.classList.replace("d-none", "d-block");
    update_title.classList.replace("d-block", "d-none");
   home_title.classList.replace("d-none", "d-block");
}*/

function clear() {
  x.value = null;
  y.value = null;
}

const reset = document.getElementById("reset");
reset.addEventListener("click", function (e) {
  e.preventDefault();
  let allData = JSON.parse(localStorage.getItem("data"));
  let filteredData = allData.filter((item) => item.Paid === 0);
  filteredData.map((item) => {
    fetch(`/ditems/${item.Id}`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);

        // Logic to remove the row from the UI
        if (data.message === "Item deleted successfully") {
          // Logic to remove the row from the UI
          updateIndex();
          //  money_left.innerHTML= `<h2> ${data.Remainder}</h2>`
        } else {
          console.error("Failed to delete item");
        }
      });
  });
});
