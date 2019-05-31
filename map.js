var myMap, coords, myPlacemark;

// Дождёмся загрузки API и готовности DOM.
ymaps.ready(init);

function init () {
    // Создание экземпляра карты и его привязка к контейнеру с
    // заданным id ("map").
    myMap = new ymaps.Map('map', {
        // При инициализации карты обязательно нужно указать
        // её центр и коэффициент масштабирования.
        center: [51.81, 107.65], // Москва
        zoom: 16
    }, {
        searchControlProvider: 'yandex#search'
    });
	
	
	coords = [51.81, 107.64];
	var 	circle1=createcircle(coords,"#DDA0DD",300);
	addcircle(myMap,circle1);
	var 	circle2=createcircle(coords,"#DA70D6",100);	
	addcircle(myMap,circle2);
	myPlacemark = new ymaps.Placemark([coords[0].toFixed(4),coords[1].toFixed(4)],{}, {preset: "twirl#redIcon", draggable: true});	
	myMap.geoObjects.add(myPlacemark);			
	
	
	//Отслеживаем событие перемещения метки
	myPlacemark.events.add("dragend", function (e) {			
			coords = this.geometry.getCoordinates();
			//myMap.geoObjects.remove(myCircle3);
			myMap.geoObjects.add(myCircle3);
			savecoordinats();
			alert(coords.join(', '));
		}, myPlacemark);

	//Отслеживаем событие щелчка по карте
	myMap.events.add('click', function (e) { 
		coords = e.get('coords'); 
		alert(coords.join(', '));
		
		circle1=createcircle(coords,"#DDA0DD",300);
		circle2=createcircle(coords,"#DA70D6",100);
		addcircle(myMap,circle1);
		addcircle(myMap,circle2);
		myMap.geoObjects.add(myCircle3);
		savecoordinats();});	

		// Обработка события, возникающего при щелчке
    // правой кнопки мыши в любой точке карты.
    // При возникновении такого события покажем всплывающую подсказку
    // в точке щелчка.
    myMap.events.add('contextmenu', function (e) {
		//coords = e.get('coordPosition'); 
		coords = e.get('coords'); 
		savecoordinats();
        myMap.hint.open(coords, 'Кто-то щелкнул правой кнопкой');
    });
    
    // Скрываем хинт при открытии балуна.
    myMap.events.add('balloonopen', function (e) {
        myMap.hint.close();
    });

	//Функция для передачи полученных значений в форму
	function savecoordinats (){	
		var new_coords = [coords[0].toFixed(4), coords[1].toFixed(4)];	
		myPlacemark.getOverlay().getData().geometry.setCoordinates(new_coords);
		document.getElementById("latlongmet").value = new_coords;
		document.getElementById("mapzoom").value = '1'; //myMap.getZoom();
		var center = myMap.getCenter();
		var new_center = [center[0].toFixed(4), center[1].toFixed(4)];	
		document.getElementById("latlongcenter").value = new_center;
		alert(coords.join(', '));
	}
	
}

function createcircle(coords,iColor,irad){
		// Создаем круг.
    var myCircle = new ymaps.Circle([
        // Координаты центра круга.
			[coords[0].toFixed(4),coords[1].toFixed(4)],
        // Радиус круга в метрах.
			irad
    ], {
        // Описываем свойства круга.
        // Содержимое балуна.
        balloonContent: "Радиус круга - 300 м",
        // Содержимое хинта.
        hintContent: "Николаевский"
    }, {
        // Задаем опции круга.
        // Включаем возможность перетаскивания круга.
      //  draggable: false,
        // Цвет заливки.
        // Последний байт (77) определяет прозрачность.
        // Прозрачность заливки также можно задать используя опцию "fillOpacity".
        fillColor: iColor,
        // Прозрачность
        fillOpacity: 0.2,
		//Толщина обводки
		strokeWidth: 0
    });
	return myCircle;
}

function addcircle(myMap,Circle){
    myMap.geoObjects.add(Circle);
}

