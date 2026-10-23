from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Station


User = get_user_model()


class StationAPITestCase(APITestCase):

    def setUp(self):

        # User for authenticated requests
        self.user = User.objects.create_user(
            username='stationuser',
            password='testpass123'
        )

        # Active station
        self.station = Station.objects.create(
            station_code='HWH',
            station_name='Howrah Junction',
            city='Howrah',
            state='West Bengal',
            is_active=True
        )

        # Another active station
        self.station2 = Station.objects.create(
            station_code='NDLS',
            station_name='New Delhi',
            city='Delhi',
            state='Delhi',
            is_active=True
        )

        # Inactive station
        self.inactive_station = Station.objects.create(
            station_code='TEST',
            station_name='Test Station',
            city='Test City',
            state='West Bengal',
            is_active=False
        )

    # --------------------------------------------------
    # TEST 1: List stations
    # --------------------------------------------------

    def test_station_list(self):

        url = reverse('station-list-create')

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            3
        )

    # --------------------------------------------------
    # TEST 2: Search by station code
    # --------------------------------------------------

    def test_search_by_station_code(self):

        url = reverse('station-list-create')

        response = self.client.get(
            url,
            {
                'station_code': 'HWH'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['station_code'],
            'HWH'
        )

    # --------------------------------------------------
    # TEST 3: Search by city
    # --------------------------------------------------

    def test_search_by_city(self):

        url = reverse('station-list-create')

        response = self.client.get(
            url,
            {
                'city': 'Howrah'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['city'],
            'Howrah'
        )

    # --------------------------------------------------
    # TEST 4: Search is case insensitive
    # --------------------------------------------------

    def test_search_case_insensitive(self):

        url = reverse('station-list-create')

        response = self.client.get(
            url,
            {
                'station_code': 'hwh'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # --------------------------------------------------
    # TEST 5: Station detail
    # --------------------------------------------------

    def test_station_detail(self):

        url = reverse(
            'station-detail',
            kwargs={'pk': self.station.id}
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['station_code'],
            'HWH'
        )

    # --------------------------------------------------
    # TEST 6: Create station requires authentication
    # --------------------------------------------------

    def test_create_station_requires_authentication(self):

        url = reverse('station-list-create')

        data = {
            'station_code': 'SDAH',
            'station_name': 'Sealdah',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'is_active': True
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # --------------------------------------------------
    # TEST 7: Authenticated user can create station
    # --------------------------------------------------

    def test_authenticated_user_can_create_station(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse('station-list-create')

        data = {
            'station_code': 'SDAH',
            'station_name': 'Sealdah',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'is_active': True
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data['station_code'],
            'SDAH'
        )

    # --------------------------------------------------
    # TEST 8: Duplicate station code not allowed
    # --------------------------------------------------

    def test_duplicate_station_code(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse('station-list-create')

        data = {
            'station_code': 'HWH',
            'station_name': 'Another Howrah',
            'city': 'Howrah',
            'state': 'West Bengal',
            'is_active': True
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            400
        )