const baseURL = 'http://localhost:5000/';

function callService1() {
  var request = new XMLHttpRequest();
  //request.withCredentials = true;
  request.open('GET', baseURL + 'test1', true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencode');
  //request.setRequestHeader('Access-Control-Allow-Credentials', true);
  request.onload = function () {
  
    // Begin accessing JSON data here
    var data = this.response;
    if (request.status >= 200 && request.status < 400) {
      document.getElementById("service1result").innerHTML += data;
    } else {
      const errorMessage = document.createElement('marquee');
      errorMessage.textContent = `Gah, it's not working!`;
    }
  }
  request.send();
}

function callService2() {
  var request = new XMLHttpRequest();
  //request.withCredentials = true;
  request.open('GET', baseURL +'test2', true);
  request.setRequestHeader('Content-Type', 'application/x-www-form-urlencode');
  //request.setRequestHeader('Access-Control-Allow-Credentials', true);
  request.onload = function () {
  
    // Begin accessing JSON data here
    var data = this.response;
    if (request.status >= 200 && request.status < 400) {
      document.getElementById("service2result").innerHTML += data;
    } else {
      const errorMessage = document.createElement('marquee');
      errorMessage.textContent = `Gah, it's not working!`;
    }
  }
  request.send();
}


