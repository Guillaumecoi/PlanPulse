from django.contrib.auth.models import User
from datetime import timedelta
from PlanPulse.course.models.models import Course


user, created = User.objects.create_user(username='testuser', password='testpassword')
course = Course.objects.create(user=user, title='Concepten van Programeertalen')

# Add metrics to the course
pages_done = course.add_metric('Pages', 'number', achievement_level='Done' , weigth=4, time_estimate=timedelta(minutes=4))
pages_summarized = course.add_metric('Pages', 'number', achievement_level='Summarized', weigth=12, time_estimate=timedelta(minutes=12))
slides_done = course.add_metric('slides', 'number', achievement_level='' , weigth=1, time_estimate=timedelta(minutes=1))

# Add chapters to the course
blok1 = course.add_chapter('Basisconcepten')
chapter1 = blok1.add_chapter('Waarden en typen')
chapter2 = blok1.add_chapter('Variabelen en geheugen')
chapter3 = blok1.add_chapter('Bindingen en scope')
chapter4 = blok1.add_chapter('Abstractie van procedures')

blok2 = course.add_chapter('Geavanceerde concepten')
chapter5 = blok2.add_chapter('Abstractie van gegevens')
chapter6 = blok2.add_chapter('Generieke abstractie')
chapter7 = blok2.add_chapter('Typesystemen')
chapter8 = blok2.add_chapter('Control flow')

blok3 = course.add_chapter('Parallel programmeren')
chapter9 = blok3.add_chapter('Parallel programmeren')
chapter10 = blok3.add_chapter('Casestudies')

blok4 = course.add_chapter('Programmeerparadigma\'s')
chapter11 = blok4.add_chapter('Imperatief programmeren')
chapter12 = blok4.add_chapter('Objectgeoriënteerd programmeren')
chapter13 = blok4.add_chapter('Functioneel programmeren')
chapter14 = blok4.add_chapter('Logisch programmeren')
chapter15 = blok4.add_chapter('Scripting')
chapter16 = blok4.add_chapter('Andere paradigma\'s en concepten')
chapter17 = blok4.add_chapter('Conclusie')


# Add metrics to the chapters
chapter1.add_progressinstance()