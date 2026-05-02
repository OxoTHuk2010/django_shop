from django.test import TestCase

from products.models import Category, Product


class ProductCatalogApiTests(TestCase):
    def setUp(self):
        self.cat_hops = Category.objects.create(name="API Hops", slug="api-hops")
        self.cat_malts = Category.objects.create(name="API Malts", slug="api-malts")
        self.p1 = Product.objects.create(
            name="Alpha Hop",
            slug="alpha-hop",
            description="api-uniq-citrus-pine",
            price="10.00",
            category=self.cat_hops,
            stock=5,
            popularity=5,
        )
        self.p2 = Product.objects.create(
            name="Beta Malt",
            slug="beta-malt",
            description="api-uniq-toffee-bread",
            price="20.00",
            category=self.cat_malts,
            stock=5,
            popularity=2,
        )
        self.p3 = Product.objects.create(
            name="Gamma Hop",
            slug="gamma-hop",
            description="api-uniq-tropical-fruit",
            price="15.00",
            category=self.cat_hops,
            stock=5,
            popularity=9,
        )

    def test_filter_by_category(self):
        response = self.client.get(f"/api/products/?category={self.cat_hops.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        slugs = {item["slug"] for item in data["results"]}
        self.assertEqual(slugs, {self.p1.slug, self.p3.slug})

    def test_search_products(self):
        response = self.client.get("/api/products/?search=api-uniq-tropical-fruit")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["slug"], self.p3.slug)

    def test_ordering_by_price_desc(self):
        response = self.client.get(f"/api/products/?category={self.cat_hops.id}&ordering=-price")
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0]["slug"], self.p3.slug)
        self.assertEqual(results[1]["slug"], self.p1.slug)

    def test_pagination_page_size_applied(self):
        for idx in range(15):
            Product.objects.create(
                name=f"Extra Product {idx}",
                slug=f"extra-product-{idx}",
                description="extra item",
                price="1.00",
                category=self.cat_hops,
                stock=1,
                popularity=0,
            )

        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["count"], 18)
        self.assertEqual(len(data["results"]), 12)
