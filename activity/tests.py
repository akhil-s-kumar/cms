from django.test import TestCase
from activity.models import News,Tags
from django.contrib.auth.models import User
class NewsTestCase(TestCase):
    def setUp(self):
        self.news = News.objects.create(
            title = "students",
            slug = "students-selected",
            pinned = "True",
            categories = "CLUB_ACHIEVEMENT",
            description = "Test_Successfull"
        )
    def test_news(self):
        self.assertEquals(self.news.title,'students')
        self.assertEquals(self.news.slug,'students-selected')
        self.assertEquals(self.news.pinned,'True')
        self.assertEquals(self.news.categories,'CLUB_ACHIEVEMENT')
        self.assertEquals(self.news.description,'Test_Successfull')