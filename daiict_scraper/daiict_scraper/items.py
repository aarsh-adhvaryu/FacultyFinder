import scrapy


class FacultyItem(scrapy.Item):
    # Core Metadata
    Name = scrapy.Field()
    University = scrapy.Field()
    Type = scrapy.Field()  
    Profile_URL = scrapy.Field()

    # Contact Info
    Email_ID = scrapy.Field()
    Contact_Number = scrapy.Field()
    Address = scrapy.Field()
    Hyperlink = scrapy.Field()  

    # Content Fields
    Education = scrapy.Field()
    Specializations = scrapy.Field()
    Biography = scrapy.Field()
    Publications = scrapy.Field()
    Teaching = scrapy.Field()
    Research = scrapy.Field()
