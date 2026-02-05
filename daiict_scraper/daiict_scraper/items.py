import scrapy


class FacultyItem(scrapy.Item):
    # Standard Fields
    University = scrapy.Field()
    Type = scrapy.Field()
    Name = scrapy.Field()
    Education = scrapy.Field()
    Contact_Number = scrapy.Field()
    Email_ID = scrapy.Field()
    Address = scrapy.Field()
    Hyperlink = scrapy.Field()
    Profile_URL = scrapy.Field()
    Photo_URL = scrapy.Field()
    Biography = scrapy.Field()
    Teaching = scrapy.Field()
    Research = scrapy.Field()
    Publications = scrapy.Field()
    Specializations = scrapy.Field()
