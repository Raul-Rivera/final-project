function keyEvents (event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        document.getElementById(event.currentTarget.selectorParam).click();
    }
}


function setIntersection(set1, set2) {
	return new Set(Array.from(set1).filter(x => set2.has(x)))
}


function GetCheckedCategoriesSet () {
	var filterCategories = new Set();
	var checkboxes = document.querySelectorAll("input[name='courseCategories']:checked")
	for (var i = 0; i < checkboxes.length; i++)
		filterCategories.add(checkboxes[i].value);
	return filterCategories;
}


function GetCourseCategoriesSet(courseObject) {
	let courseCategorySet = new Set (courseObject.getAttribute('data-categories').replace(/[\[|\]]/g,"").split(","));
	return courseCategorySet;
}


function filterCoursesByCategory(category) {
    var id = category.getAttribute('data-categoryid');
 	var checkboxes = document.querySelectorAll("input[name='courseCategories']");
 	if (id === '0') {
 		let checked = category.checked;
		for (var i = 1; i < checkboxes.length; i++)
			checkboxes[i].checked = checked;
 	} else {
		if (!category.checked)
			checkboxes[0].checked = false;
		else {
			let count = 0;
			for (var i = 1; i < checkboxes.length; i++)
				if (checkboxes[i].checked)
					count++;
			if (count == checkboxes.length-1)
				checkboxes[0].checked = true;
		}
 	}

	var filterCategories = GetCheckedCategoriesSet();
	document.querySelectorAll('[data-selector="course-entry"]').forEach ( course => {
		if (id==0)
			if (category.checked)
				course.classList.remove("d-none");
			else
				course.classList.add("d-none");
		else {
			let courseCategorySet = GetCourseCategoriesSet(course);
			let canditateCourse = (setIntersection(courseCategorySet, filterCategories).size > 0);
			if (canditateCourse)
				course.classList.remove("d-none");
			else
				course.classList.add("d-none");
		}
	});
}


function filterCoursesByString(filterstring) {
	var filterCategories = GetCheckedCategoriesSet();

    document.querySelectorAll('[data-selector="course-entry"]').forEach ( course => {
		var courseCategorySet = GetCourseCategoriesSet(course);
		var candidateCourse = (setIntersection(courseCategorySet, filterCategories).size > 0);
		if (!filterstring) {
			if (candidateCourse)
				course.classList.remove("d-none");
			else
				course.classList.add("d-none");
		} else {
			if (candidateCourse) {
				let content = course.getAttribute('data-content');
				let wordslist = filterstring.replace(/\[\],\.#\$%&\/\\@~!\?¿-_\+\^\*{}\|]/g,"").split (" ");
				let matchedwords = wordslist.filter(word => content.includes(word));
				if (matchedwords && matchedwords.length > 0)
					course.classList.remove("d-none");
				else
					course.classList.add("d-none");
			}
		}
	});
}


function getAddsInfo (courseid) {
	let addsList = document.querySelectorAll('input'+`.check-${courseid}`+'[type="checkbox"]');
	var freeAdds = 0;
	var extrapriceAdds = 0;

    addsList.forEach( add => {
		if (add.checked) {
			if (add.getAttribute('data-free').toLowerCase() == 'true')
				freeAdds++;
			else
				extrapriceAdds += parseFloat(add.getAttribute('data-extraprice'));
		}
	});
	response = {"list": addsList,
				"numberfree": freeAdds,
				"extraprice": extrapriceAdds }
	return response;
}


function updateOrderCoursePrice (courseid) {
    let cprice = parseFloat(document.querySelector(`#modal-${courseid}-coursePrice`).getAttribute('value'));
	let adds = getAddsInfo (courseid);
    totalPrice = cprice + adds.extraprice;

    document.querySelector(`#modal-${courseid}-coursePrice`).innerHTML = totalPrice.toFixed(2);
    return adds;
}


function checkOrderAdds (courseid) {
	let maxAdds = document.querySelector(`#modal-${courseid}-courseAdds`).getAttribute('value');
	let adds = updateOrderCoursePrice (courseid);
	let addsList = adds.list;
	let numAdds = adds.numberfree;

    document.querySelector(`#modal-${courseid}-courseAdds`).innerHTML = `${maxAdds-numAdds}`;

	if (numAdds == maxAdds) {
		addsList.forEach ( add => {
			if (!add.checked && add.getAttribute('data-free').toLowerCase() == 'true')
				add.disabled = true;
		});
	} else if (numAdds < maxAdds) {
		addsList.forEach ( add => {	if (add.disabled) add.disabled = false; });
	}
}


document.addEventListener('DOMContentLoaded', load);


function load () {
	document.querySelectorAll("input[name='courseCategories']").forEach ( category => {
		category.addEventListener('click', event => {
			filterCoursesByCategory(category)
		});
	});

	document.querySelectorAll("input[name='courseAdds']").forEach ( add => {
		add.addEventListener('change', event => {
			checkOrderAdds(add.getAttribute('data-courseid'));
		});
	});

	var stringInputField = document.querySelector("#filterString");
	if (typeof stringInputField !== 'undefined' && stringInputField != null) {
	    stringInputField.addEventListener("keyup", keyEvents, false);
	    stringInputField.selectorParam = 'filterButton';
		document.querySelector("#filterButton").addEventListener('click', event => {
	  		filterCoursesByString(stringInputField.value);
		});

		document.querySelector("#clearButton").addEventListener('click', event => {
			stringInputField.value='';
	  		filterCoursesByString("");
		});
	}

	function setRatingStar(starRating) {
		starRating.forEach ( item => {
			if (parseInt(item.parentNode.querySelector('input#userrating').value) >= parseInt(item.getAttribute('data-rating')))
			  item.classList.add('checked');
			else
			  item.classList.remove('checked');
		});
	}

	document.querySelectorAll (".starsBox > i").forEach ( item => {
		item.addEventListener('click', event => {
			item.parentNode.querySelector('input#userrating').value = item.getAttribute('data-rating');
			setRatingStar(item.parentNode.querySelectorAll (".starsBox > i"));
		});
	});

	document.querySelectorAll('.starsBox > button#clear').forEach ( item => {
		item.addEventListener('click', event => {
			item.parentNode.querySelector('input#userrating').value = 0;
		  	item.parentNode.querySelectorAll (".starsBox > i").forEach ( item => {
				item.classList.remove('checked');
			});
		});
    });

	setRatingStar(document.querySelectorAll (".starsBox > i"));
	csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

}
