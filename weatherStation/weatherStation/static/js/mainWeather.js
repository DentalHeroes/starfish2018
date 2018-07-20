
function    getLocation() {
	//make an ajax call to an ip geolocation api
	$.ajax({
		url:"http://gd.geobytes.com/GetCityDetails?callback=?&filter=US",
		dataType: 'json',
		success: function (data, status) {
			if(status === "success") {
				if(data.geobyteslatitude) {
					var locationType = 'lat=' + data.geobyteslatitude + '&lon=' + data.geobyteslongitude;
					getWeather(locationType);
				} else {
					alert("IP Geolocation unavailable.  Please use zip code.");
				}
			}else {
					alert("IP Geolocation unavailable.  Please use zip code.");
			}
		},
		error: function (error){
			alert("IP Geolocation unavailable.  Please use zip code.");
		}
	});
}

	//Makes an ajax call to the openweather api
function	getWeather(locationType) {
	//store locationType into a hidden field for refreshing weather
	$('#locationType').val(locationType);
	//bind the WeatherWrapper element to a variable
	var wrapper = $("#WeatherWrapper");
	//clear the wrapper of any content
	wrapper.empty();
	$.ajax({
		url: 'https://api.openweathermap.org/data/2.5/weather?' + locationType + '&appid=3c90ef0d527512b433ebf00ac0321e72',
		type: 'GET',
		dataType: 'jsonp',
		success: function (data) {
			
			//create the sensor data content and append it to the wrapper
			wrapper.append(createWeatherWidg(data));
		},
		error: function (error) {
			alert('Failed!');
		}
	});
}

//retrieves stored locationType and uses it to getWeather
function refreshWeather(){
	var locationType = $('#locationType').val();
	getWeather(locationType);
}


function clearLoadingScreen(){
	//show the outside-weather-container by removing the 'hidden' css class
	$('#outside-weather-container').removeClass('hidden');
	//show the alert-wrapper by removing the 'hidden' css class
	 $('#alert-wrapper').removeClass('hidden');
	 //hide the loading content by adding the 'hidden' css class
	$('#loading').addClass('hidden');
}

	// uses ajax call to get sensor data
function    getSensorData() {
	$.ajax({
		// notice how the url is different. It doesn't include 'http://' which
		// tells us that we're calling an API on our internal server.
		url: '/sensor',
		type: 'GET',
		dataType: 'json',
		success: function (data) {
			//bind the SensorDataWrapper element to a variable
			var wrapper = $("#SensorDataWrapper");
			//clear the wrapper of any content
			wrapper.empty();
			//create the sensor data content and append it to the wrapper
			wrapper.append(createSensorDataWidg(data));
			clearLoadingScreen();
		},
		error: function (error) {
			alert('Failed!');			
			//create refresh button
			var button = '<p><button id="submitZip" onclick="refreshSensor()" class="btn btn-primary" >Refresh</button></p>';
			//bind the SensorDataWrapper element to a variable
			var wrapper = $("#SensorDataWrapper");
			//clear the wrapper of any content
			wrapper.empty();
			//create the sensor data content and append it to the wrapper
			wrapper.append(button);
		}
	});
}


function refreshSensor(){
	//bind the SensorDataWrapper element to a variable
	var wrapper = $("#SensorDataWrapper");
	//clear the wrapper of any content
	wrapper.empty();
	wrapper.append(getLoading());
	getSensorData()
	
}
	
function getLoading(){
return '<div id="SensorDataWrapper" class="col-xs-12">' +
			 '<div id="loading" class="col-xs-12 col-sm-8">' +
				'<span class="fas fa-spinner fa-spin"></span>' +
				'<p>Loading...</p>' +
			'</div>' +
       '</div>';	
}	
	
//Uses a switch statement to map different weather 
//conditions to their appropriate weather icon
//conditions taken from api documentaion
//https://openweathermap.org/weather-conditions
function	mapWeather(description, isDay) {
	switch (description) {
		case 'clear sky':
			if (isDay) {
				return {
					icon: '<span id="weather-icon" class="fas fa-sun"></span>'
				}
			} else {
				return {
					icon: '<span id="weather-icon" class="fas fa-moon"></span>'
				}
			}
		case 'few clouds':
			return {
				icon: '<span id="weather-icon" class="fas fa-cloud"></span>'
			}
		case 'scattered clouds':
		case 'broken clouds':
		case 'mist':
		case 'overcast clouds':
			return {
				icon: '<span id="weather-icon" class="fas fa-cloud"></span>'
			}
		case 'shower rain':
		case 'rain':
		case 'light rain':
		case 'moderate rain':
		case 'light intensity drizzle':
		case 'drizzle':
		case 'heavy intensity drizzle':
		case 'light intensity drizzle rain':
		case 'drizzle rain':
		case 'heavy intensity drizzle rain':
		case 'shower rain and drizzle':
		case 'heavy shower rain and drizzle':
		case 'shower drizzle':
		case 'heavy intensity rain':
		case 'very heavy rain':
		case 'extreme rain':
		case 'freezing rain':
		case 'light intensity shower rain':
		case 'shower rain':
		case 'heavy intensity shower rain':
		case 'ragged shower rain':		
			return {
				icon: '<span id="weather-icon" class="fas fa-tint"></span>'
			}
		case 'thunderstorm':
		case 'thunderstorm with heavy rain':
		case 'thunderstorm with rain':
		case 'thunderstorm with light rain':
		case 'light thunderstorm':
		case 'heavy thunderstorm':
		case 'ragged thunderstorm':
		case 'thunderstorm with light drizzle':
		case 'thunderstorm with drizzle':
		case 'thunderstorm with heavy drizzle':
			return {
				icon: '<span id="weather-icon" class="fas fa-bolt"></span>'
			}
		case 'snow':
		case 'light snow':
		case 'heavy snow':
		case 'sleet':
		case 'shower sleet':
		case 'light rain and snow':
		case 'rain and snow':
		case 'light shower snow':
		case 'shower snow':
		case 'heavy shower snow':
			return {			
				icon: '<span id="weather-icon" class="fas fa-snowflake"></span>'
			}
		default:
			return{
				icon: '<span id="weather-icon" class=""></span>'
			}
	}
}

function	createWeatherWidg(data) {
				
	var isDay = this.isDaytime(new Date(data.sys.sunrise), new Date(data.sys.sunset));
	var mappedData = this.mapWeather(data.weather[0].description, isDay);
	var location = data.name;

	$('#weather-icon').replaceWith(mappedData.icon);
	$('#weather-desc').text(data.weather[0].description);
	$('#weather-location').text(location);

	return "<p class='title'>Outside</p>" +
			//convert Kelvin to farenheit
			"<p>Temperature: " + (data.main.temp  * 9/5 - 459.67).toFixed(2) + " F</p>"+
			"<p>Wind Speed: " + data.wind.speed + "</p>" +
			"<p>Humidity: " + data.main.humidity + "%</p>" +
			//convert hectopascals to inches of mercury
			"<p>Pressure: " + (data.main.pressure/ 33.863886666667).toFixed(2) + " in</p>" +
			'<p><button id="submitZip" onclick="refreshWeather()" class="btn btn-primary" >Refresh</button></p>';
}

function	createSensorDataWidg(data) {
	return "<p class='title'>Inside</p>" +
			//if temp is zero then output zero, otherwise convert celcius to farenheit
		   "<p>Temperature: " + (data.temp === 0 ? 0 : ((data.temp * 9 / 5) + 32).toFixed(2)) + " F</p>" +
		   "<p>Humidity: " + data.humidity + "%</p>" +
		   '<p><button id="submitZip" onclick="refreshSensor()" class="btn btn-primary" >Refresh</button></p>';
}

			// compares the current time to sunrise and sunset times
			// to determine if it is currently daytime
function	isDaytime(sunrise, sunset) {
	var current = new Date();
	var currentSec = this.getDaySeconds(current);
	var sunriseSec = this.getDaySeconds(sunrise);
	var sunsetSec = this.getDaySeconds(sunset);

	return currentSec > sunriseSec && currentSec < sunsetSec;
}

			//converts a current time into the number of total seconds since 12 am
function	getDaySeconds(time) {
	return time.getSeconds() + (60 * (time.getMinutes() + (60 * time.getHours())))
}
	
	
 

var images = [];

//add all of the images in the assets folder to the image array
function setImageArray(arr) {
    arr.forEach(function(imageUrl) {
        var image = new Image();
        image.id = 'background-image';
        image.src = '/static/assets/' + imageUrl;
        images.push(image);
    })
};


function getBackgroundImage() {
	//generate a random number from 0 to the number of images in the image array
    var whichImage = Math.round(Math.random()*(images.length-1));
	//set the background with a random image
    $('#background-image').replaceWith(images[whichImage])
};


function sendAlert() {
	//uses ajax to send an http Get request to the Alert API
    $.ajax({
	// notice how the url is different. It doesn't include 'http://' which
	// tells us that we're calling an API on our internal server.
        url: '/alert',
        type: 'GET'
    });
};


function getWeatherLocation(){
	//get zipcode from user input
	var zipcode = $('#zip').val();
	
	//check if a zipcode was entered
	if (zipcode.length === 0){
		//if no zipcode was entered get location from ip
		getLocation();
	}
	//if zipcode is not valid 5 digit number alert user
	else if (isNaN(zipcode) || zipcode.length !== 5 ){
		alert("Please enter a valid zipcode");
		//clear out zipcode field
		$('#zip').val();
	} else {
		//get weather with valid zipcode
		var locationType = 'zip=' + zipcode + ',us';
		getWeather(locationType);
	}
	
}
