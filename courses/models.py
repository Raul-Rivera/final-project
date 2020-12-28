from django.contrib.auth.models import AbstractUser
from django.db.models import Q, Sum, Count
from django.db import models


class User(AbstractUser):
	def get_activeOrders(self):
		return self.orders.filter(active=True)

	def __str__(self):
		return f"{self.username} ({self.email})"


class DistribCourse(models.Model):
	name = models.CharField(max_length=128)
	active = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.name}"


class Course(models.Model):
	name = models.CharField(max_length=128)
	description = models.CharField(max_length=512)
	image = models.CharField(max_length=256)
	price = models.FloatField(default=0.00)
	maxFreeAdds = models.IntegerField(default=0)
	provider = models.ForeignKey(DistribCourse, on_delete=models.PROTECT, default=1, blank=True)
	avgRating = models.FloatField(default=0.0)
	active = models.BooleanField(default=True)

	def get_avgRating_int(self):
		return int(self.avgRating)

	def __str__(self):
		return f"[{self.name}] maxFreeAddsfree({self.maxFreeAdds}) (${self.price}) active[{self.active}]"


class CategoCourse(models.Model):
	name = models.CharField(max_length=64)
	courses = models.ManyToManyField(Course,related_name="categories", blank=True)

	def __str__(self):
		return f"{self.name}"


class AddCourse(models.Model):
	name = models.CharField(max_length=128)
	free = models.BooleanField(default=False)
	extraprice = models.FloatField(default=0.00)
	course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="adds", blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return f"[{self.name}] --{self.free}--(${self.extraprice}) active[{self.active}]"


class ReviCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    text = models.CharField(max_length=256,default='')
    rating = models.IntegerField(default=0)

    class Meta:
    	constraints = [
    		models.UniqueConstraint(fields=['course','user'], name='course-user-compositekey')
    	]

    def __str__(self):
    	return f"{self.course.name}--{self.user.username} ({self.rating}) [{self.text}]"


class Order(models.Model):
	datetime = models.DateTimeField(auto_now=False, auto_now_add=True)
	client = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
	price = models.FloatField(default=0.00)
	active = models.BooleanField(default=True)

	def get_orderCode (self):
		return "{date}-{id:03d}".format(date=self.datetime.strftime("%Y-%m"), id=self.id)

	def __str__(self):
		return f"({self.id}) Dt[{self.datetime}] {self.client.username} {self.price} active[{self.active}] nItems({self.items.count()})"


class OrderCourse(models.Model):
	course = models.ForeignKey(Course, related_name="orders", on_delete=models.CASCADE, default=1, blank=True)
	quantity = models.IntegerField(default=0)
	price = models.FloatField(default=0.00)
	order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)

	def get_subitemsPrice (self):
		response = self.subitems.all().aggregate(
				extraprices=Sum('extraprice',filter=Q(add__free=False)),
				numcharged=Count('add',filter=Q(add__free=False)),
				numfree=Count('add',filter=Q(add__free=True))
			)
		return {
				'extraprices': response["extraprices"] or 0,
				'numcharged':response["numcharged"],
				'numfree':response["numfree"]
			}

	def __str__(self):
		return f"({self.id}) Course[{self.course.name}] Q({self.quantity}) (${self.price}) ParentOrder({self.order.id}) nSubitems({self.subitems.count()})"


class OrderSubitem(models.Model):
	add = models.ForeignKey(AddCourse, on_delete=models.CASCADE)
	extraprice = models.FloatField(default=0.00)
	item = models.ForeignKey(OrderCourse, related_name="subitems", on_delete=models.CASCADE)

	def __str__(self):
		return f"({self.id}) add[{self.addcod.name}] (${self.extraprice}) ParentItem({self.item.id})"
