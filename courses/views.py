import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db import IntegrityError, Error
from django.db.models import Avg
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from .models import User, Course, CategoCourse, AddCourse, ReviCourse, Order, OrderCourse, OrderSubitem


def error404 (request, exception):
	pagename = request.get_full_path().split("/").pop()
	response = render(request, 'notfound.html', {
		"message": "The resource you are looking for does not exist.",
		"pagename": pagename
	})
	response.status_code = 404
	return response


def index (request):
	if request.user.is_authenticated:
		usrCurrent = User.objects.get(username=request.user.username)
	else:
		usrCurrent = None
	return render(request, "courses/index.html", {
		"catalog": Course.objects.filter(active=True),
		"categories": CategoCourse.objects.order_by('name'),
		"user": usrCurrent,
	})


def login_view(request):
	if request.method == "POST":
		username = request.POST["username"]
		password = request.POST["password"]
		usr = authenticate(request, username=username, password=password)
		if usr is not None:
			login(request, usr)
			return HttpResponseRedirect(reverse("index"))
		else:
			return render(request, "courses/login.html", {"message": "Invalid credentials.", "msgType":"alert-danger"})
	else:
		return render(request, "courses/login.html")


def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse("index"))


def register(request):
	if request.method == "POST":
		username = request.POST['username']
		email = request.POST['email']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		password = request.POST["password"]
		confirmation = request.POST["confirmation"]
		if password != confirmation:
			return render(request, "courses/register.html", {"message": "Passwords must match.","msgType":"alert-warning"})

		try:
			usr = User.objects.create_user(username, email, password)
			usr.first_name = firstname
			usr.last_name = lastname
			usr.save()
		except IntegrityError:
			return render(request, "courses/register.html", {"message": "Username already taken.", "msgType":"alert-warning"})

		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request, "courses/register.html")


def coursereview (request, idcourse=None):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))
	usrCurrent = User.objects.get(username=request.user.username)
	if request.method == "GET":
		course = Course.objects.get(id=idcourse)
		ur = ReviCourse.objects.filter(course=course,user=usrCurrent)
		if ur.exists():
			ur = ur.first()
			userReview = {'text': ur.text, 'rating': ur.rating }
		else:
			userReview = {'text':'', 'rating':0}
		courseReviews = ReviCourse.objects.exclude(user=usrCurrent).filter(course=course)
		return render(request, "courses/coursereview.html", {"course": course, "userReview": userReview, "courseReviews": courseReviews})
	elif request.method == "POST":
		courseId = request.POST.get('idcourse', None)
		course = Course.objects.get(id=courseId)
		if not courseId:
			return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "No id_courses"})
		userRating = request.POST.get('userrating', None)
		userReview = request.POST.get('userreview', None)
		action = request.POST.get ('buttonAction', None)

		if action in "update":
			rating, created = ReviCourse.objects.update_or_create(
				course=course, user=usrCurrent,
				defaults={'rating': userRating, 'text': userReview}
			)
		elif action in "delete":
			try:
				ReviCourse.objects.filter(course=course, user=usrCurrent).delete()
			except IntegrityError:
				return render(request, "courses/register.html", {"message": "Integrity error.", "msgType":"alert-warning"})
		else:
			return render(request, "courses/error.html", {"msgType": "alert-danger", "message": f'Invalid operation - Unknown botton action: {action}'})

		course.avgRating = float(ReviCourse.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg'])
		course.save()
		return HttpResponseRedirect(reverse("index"))
	else:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": 'Bad request!'})


def addcart(request):
	if request.method != "POST":
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "Only POST request allowed"})

	courseId = request.POST.get('idcourse', None)
	if not courseId:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "No id_courses"})

	addsList = request.POST.getlist('courseAdds',None)

	try:
		course = Course.objects.get(pk=courseId)
	except KeyError:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "Key error."})
	except course.DoesNotExist:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "Course do not exist."})

	productQ = 1
	usrCurrent = User.objects.get(username=request.user.username)

	order  = Order()
	order.client = usrCurrent
	order.price = 0
	order.active = True
	order.save()

	ordItem = OrderCourse()
	ordItem.course = course
	ordItem.quantity = productQ
	ordItem.price = course.price
	ordItem.order = order
	ordItem.save()

	extrapricesAdds = 0
	for a in addsList:
		params = a.split("-")
		addExtraprice = float(params[1])
		addId = int(params[0])
		extrapricesAdds += addExtraprice
		ordSubitem = OrderSubitem()
		try:
			ordSubitem.add = AddCourse.objects.get(id=addId)
		except KeyError:
			return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "AddCourse Key error."})
		except AddCourse.DoesNotExist:
			return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "AddCourse do not exist."})
		ordSubitem.extraprice = addExtraprice
		ordSubitem.item = ordItem
		ordSubitem.save()

	order.price = (course.price + extrapricesAdds) * productQ
	order.save()

	return HttpResponseRedirect(reverse("index"))


def removecart(request):
	if request.method != "POST":
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "Only POST request allowed"})

	orderId = request.POST.get('idorder', None)
	if not orderId:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "No id_order"})

	try:
		Order.objects.filter(pk=orderId).delete()
	except IntegrityError:
		return render(request, "courses/register.html", {"message": "Integrity error.", "msgType":"alert-warning"})

	return HttpResponseRedirect(reverse("displaycart"))


def displaycart(request):
	if request.method != "GET":
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "Only GET request allowed"})

	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))

	try:
		usrCurrent = User.objects.get(username=request.user.username)
	except usrCurrent.DoesNotExist:
		return render(request, "courses/error.html", {"msgType": "alert-danger", "message": "User do not exist."})

	orders = Order.objects.filter(active=True,client=usrCurrent.id)
	return render(request, "courses/shoppingcart.html", {"orders":orders})


def showpurchase(request):
    return render(request, "courses/showpurchase.html")
