import unittest
from candidates import load, page_candidates


class AssetReadiness(unittest.TestCase):
    def test_missing_product_photo_is_not_silently_substituted(self):
        source = load('directions.json')
        accepted, excluded = page_candidates(source, 'physical-product', set())
        self.assertNotIn('hero-object', {x['id'] for x in accepted})
        self.assertIn('hero-object', {x['id'] for x in excluded})
        accepted, _ = page_candidates(source, 'physical-product', {'product-photo'})
        self.assertIn('hero-object', {x['id'] for x in accepted})

    def test_picture_led_direction_needs_declared_photography(self):
        source = load('directions.json')
        accepted, _ = page_candidates(source, 'hospitality', set())
        self.assertFalse(any(x.get('needsPictures') for x in accepted))
        accepted, _ = page_candidates(source, 'hospitality', {'photography'})
        self.assertTrue(any(x.get('needsPictures') for x in accepted))

    def test_no_feasible_direction_means_empty_instead_of_random_fallback(self):
        fixture = [{'id': 'only', 'sectors': ['other'], 'needs': ['video']}]
        accepted, excluded = page_candidates(fixture, 'other', set())
        self.assertEqual(accepted, [])
        self.assertEqual(excluded[0]['missingDeclaredAssets'], ['video'])


if __name__ == '__main__':
    unittest.main()
