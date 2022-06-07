


function search(e) {
  e.preventDefault();
  e.stopPropagation();
  query = document.getElementById('search').value;
  list = document.getElementById('ul')
  option = document.getElementById('option').value
  count = document.getElementById('count').value
  list.innerHTML = ""
  let socket = new WebSocket("ws://localhost:8765");
  q_el = document.getElementById('query')
  socket.onopen = function(e) {
    // alert("[open] Connection established");
    // alert("Sending to server");
    socket.send(JSON.stringify({
      query: query,
      action: "search",
      dataset: option,
      count: count
    }));
  };
  
  socket.onmessage = function(event) {
    // alert(`[message] Data received from server: ${event.data}`);
    var arr = JSON.parse(event.data);
    content = ""
    console.log(arr);
    arr[0].forEach(el => content += cardBuilder(el.doc_name))
    // Object.keys(JSON.parse(event.data)).forEach(key => content += `<li onclick="getDetail('${key}')">${key}</li>`)
    list.innerHTML = content 
    q_el.innerHTML = "<b>Did you mean:</b><i>" + arr[1] + "</i>"
  };
  
  socket.onclose = function(event) {
    if (event.wasClean) {
      // alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
      // e.g. server process killed or network down
      // event.code is usually 1006 in this case
      // alert('[close] Connection died');
    }
  };
  
  socket.onerror = function(error) {
    alert(`[error] ${error.message}`);
  };
  
}

function getDetail(data) {
  let socket = new WebSocket("ws://localhost:8765");
  let title = document.getElementById('exampleModalLongTitle')
  title.innerHTML = data
  let body = document.getElementById('modal-body')
  option = document.getElementById('option').value
  // doc.innerHTML = ""
  socket.onopen = function(e) {
    // alert("[open] Connection established");
    // alert("Sending to server");
    socket.send(JSON.stringify({
      fileName: data,
      action: "getDetails",
      dataset: option
    }));
  };
  socket.onmessage = function(event) {
    // alert(`[message] Data received from server: ${event.data}`);
    // doc.innerHTML = JSON.parse(event.data).content
    body.innerHTML = JSON.parse(event.data).content;
    console.log(JSON.parse(event.data));
  };
  
  socket.onclose = function(event) {
    if (event.wasClean) {
      // alert(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
      // e.g. server process killed or network down
      // event.code is usually 1006 in this case
      // alert('[close] Connection died');
    }
  };
  
  socket.onerror = function(error) {
    alert(`[error] ${error.message}`);
  };
}

const searchFocus = document.getElementById('search-focus');
const keys = [
  { keyCode: 'AltLeft', isTriggered: false },
  { keyCode: 'ControlLeft', isTriggered: false },
];

window.addEventListener('keydown', (e) => {
  keys.forEach((obj) => {
    if (obj.keyCode === e.code) {
      obj.isTriggered = true;
    }
  });

  const shortcutTriggered = keys.filter((obj) => obj.isTriggered).length === keys.length;

  if (shortcutTriggered) {
    searchFocus.focus();
  }
});

window.addEventListener('keyup', (e) => {
  keys.forEach((obj) => {
    if (obj.keyCode === e.code) {
      obj.isTriggered = false;
    }
  });
});

function cardBuilder(title) {
  return `
  <div class="card mb-2">
  <div class="card-body">
    <h5 class="card-title">${title}</h5>
    <h6 class="card-subtitle mb-2 text-muted">Card subtitle</h6>
    <p class="card-text">Some quick example text to build on the card title and make up the bulk of the card's content.</p>
    <button onclick="getDetail('${title}')" type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModalCenter">
        view document
    </button>
  </div>
</div>
`
}