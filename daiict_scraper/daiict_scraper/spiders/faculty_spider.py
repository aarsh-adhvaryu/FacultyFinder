import scrapy
from ..items import FacultyItem
from w3lib.html import remove_tags


class DaiictSpider(scrapy.Spider):
    name = "faculty_spider"
    allowed_domains = ["daiict.ac.in"]

    # Mapping URLs to Faculty Types
    start_urls_map = {
        "https://www.daiict.ac.in/faculty": "Regular Faculty",
        "https://www.daiict.ac.in/adjunct-faculty": "Adjunct Faculty",
        "https://www.daiict.ac.in/adjunct-faculty-international": "International Adjunct Faculty",
        "https://www.daiict.ac.in/distinguished-professor": "Distinguished Faculty",
        "https://www.daiict.ac.in/professor-practice": "Professor of Practice",
    }

    def start_requests(self):
        for url, f_type in self.start_urls_map.items():
            yield scrapy.Request(url, callback=self.parse_list, meta={"type": f_type})

    def parse_list(self, response):
        faculty_type = response.meta["type"]

        # Selector for the faculty card
        faculty_cards = response.css("div.facultyDetails")
        self.logger.info(f"Found {len(faculty_cards)} profiles for {faculty_type}")

        for card in faculty_cards:
            profile_link = card.css("h3 a::attr(href)").get()
            list_view_spec = self.clean_html(card.css(".areaSpecialization").get())

            if profile_link:
                yield response.follow(
                    profile_link,
                    callback=self.parse_profile,
                    meta={"type": faculty_type, "fallback_spec": list_view_spec},
                )
            else:
                yield self.parse_card_only(
                    card, faculty_type, response.url, list_view_spec
                )

    def parse_profile(self, response):
        item = FacultyItem()
        item["University"] = "DA-IICT"
        item["Type"] = response.meta["type"]
        item["Profile_URL"] = response.url

        # Basic Info
        item["Name"] = self.get_text(response, ".field--name-field-faculty-names::text")
        item["Education"] = self.get_text(
            response, ".field--name-field-faculty-name::text"
        )
        item["Contact_Number"] = self.get_text(
            response, ".field--name-field-contact-no::text"
        )
        item["Address"] = self.get_text(response, ".field--name-field-address::text")

        # Email & Web
        email = response.css(".field--name-field-email .field__item::text").get()
        item["Email_ID"] = email.strip() if email else "N/A"

        web_link = response.css(".field--name-field-sites a::attr(href)").get()
        if not web_link:
            web_link = response.css(".social-media-sharing a::attr(href)").get()
        item["Hyperlink"] = web_link if web_link else "N/A"

        # Content
        item["Biography"] = self.clean_html(
            response.css(".field--name-field-biography").get()
        )
        item["Teaching"] = self.clean_html(
            response.css(".field--name-field-teaching").get()
        )
        item["Publications"] = self.clean_html(
            response.css(".education.overflowContent").get()
        )

        # Research/Specialization Logic
        spec_xpath = "//h2[contains(text(), 'Specialization')]/parent::div/following-sibling::div[contains(@class, 'work-exp')]"
        detail_spec = self.clean_html(response.xpath(spec_xpath).get())

        if detail_spec and detail_spec != "N/A":
            item["Specializations"] = detail_spec
        else:
            item["Specializations"] = response.meta.get("fallback_spec", "N/A")

        res_xpath = "//h2[contains(text(), 'Research') or contains(text(), 'Interest')]/parent::div/following-sibling::div"
        item["Research"] = self.clean_html(response.xpath(res_xpath).get())

        yield item

    def parse_card_only(self, card, f_type, url, spec):
        item = FacultyItem()
        item["University"] = "DA-IICT"
        item["Type"] = f_type
        item["Profile_URL"] = url
        item["Name"] = card.css("h3 a::text").get(default="N/A").strip()
        item["Specializations"] = spec
        for field in [
            "Education",
            "Contact_Number",
            "Email_ID",
            "Address",
            "Hyperlink",
            "Publications",
            "Teaching",
            "Research",
            "Biography",
        ]:
            item[field] = "N/A"
        return item

    def get_text(self, response, selector):
        text = response.css(selector).get()
        return text.strip() if text else "N/A"

    def clean_html(self, html_content):
        if not html_content:
            return "N/A"
        text = remove_tags(html_content)
        return " ".join(text.split())
