from django.test import TestCase
from django.urls import reverse

from .models import Train


class TrainAPITestCase(TestCase):

    def setUp(self):

        self.train = Train.objects.create(
            train_number='12345',
            train_name='Test Express',
            source_station='Howrah',
            destination_station='New Delhi',
            departure_time='10:00:00',
            arrival_time='18:00:00',
            total_seats=100,
            is_active=True
        )

        self.inactive_train = Train.objects.create(
            train_number='54321',
            train_name='Inactive Express',
            source_station='Howrah',
            destination_station='New Delhi',
            departure_time='12:00:00',
            arrival_time='20:00:00',
            total_seats=100,
            is_active=False
        )

    # TEST 1: Search by source and destination

    def test_train_search(self):

        url = reverse('train-search')

        response = self.client.get(
            url,
            {
                'source': 'Howrah',
                'destination': 'New Delhi'
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]['train_number'],
            '12345'
        )

    # TEST 2: Search should be case insensitive

    def test_train_search_case_insensitive(self):

        url = reverse('train-search')

        response = self.client.get(
            url,
            {
                'source': 'howrah',
                'destination': 'new delhi'
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

    # TEST 3: Inactive train should not appear

    def test_inactive_train_not_returned(self):

        url = reverse('train-search')

        response = self.client.get(
            url,
            {
                'source': 'Howrah',
                'destination': 'New Delhi'
            }
        )

        self.assertEqual(response.status_code, 200)

        for train in response.data:
            self.assertTrue(train['is_active'])

    # TEST 4: No matching train

    def test_no_train_found(self):

        url = reverse('train-search')

        response = self.client.get(
            url,
            {
                'source': 'Kolkata',
                'destination': 'Mumbai'
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data),
            0
        )