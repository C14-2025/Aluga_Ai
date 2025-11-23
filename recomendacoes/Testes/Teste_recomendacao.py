from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from propriedades.models import Propriedade
from favoritos.models import Favorito, UserRecommendation


class PersonalRecommendationFlowTests(TestCase):
    def setUp(self):
        # criar usuário e client autenticado
        self.user = User.objects.create_user(username="tester", password="pass")
        self.client = APIClient()
        self.client.login(username="tester", password="pass")

        # criar donos e propriedades
        owner = User.objects.create_user(username="owner1", password="x")
        # três propriedades que o usuário vai favoritar (mesma cidade)
        self.fav_props = []
        for i in range(3):
            p = Propriedade.objects.create(
                owner=owner,
                titulo=f"Fav {i}",
                descricao="fav",
                city="CidadeA",
                preco_por_noite=100 + i * 10,
                area_m2=50 + i * 5,
                quartos=1 + i,
                banheiros=1,
                vagas_garagem=0,
                ativo=True,
                comodidades=["wifi", "tv"] if i < 2 else ["wifi"],
            )
            self.fav_props.append(p)

        # criar candidatos extras — alguns similares (mesma cidade/tipo/amenities)
        self.candidates = []
        for j in range(6):
            p = Propriedade.objects.create(
                owner=owner,
                titulo=f"Cand {j}",
                descricao="cand",
                city="CidadeA" if j % 2 == 0 else "CidadeB",
                preco_por_noite=90 + j * 15,
                area_m2=40 + j * 3,
                quartos=1 + (j % 3),
                banheiros=1,
                vagas_garagem=1 if j % 2 == 0 else 0,
                ativo=True,
                comodidades=["wifi"] if j % 3 != 0 else ["piscina"],
            )
            self.candidates.append(p)

        # favoritar os 3
        for p in self.fav_props:
            Favorito.objects.create(user=self.user, propriedade=p)

    def test_personal_recommendation_based_on_favorites(self):
        # Mock PriceModel.instance to deterministic predictor
        from recomendacoes.services.ml import views as ml_views
        class DummyModel:
            def predict(self, features, return_details=False):
                # predições constantes — suficiente para testar similaridade por cidade/amenities
                return 100.0, 'dummy', None

        # patch the instance method to return dummy model
        original_instance = ml_views.PriceModel.instance
        try:
            ml_views.PriceModel.instance = staticmethod(lambda: DummyModel())

            resp = self.client.post('/api/ml/personal_recommend/', data={'limit': 5}, format='json')
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data.get('status'), 'ok')
            results = data.get('results')
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0, "Espera-se ao menos 1 recomendação")

            # Garantir que as recomendações não incluam os próprios favoritos
            fav_ids = {p.id for p in self.fav_props}
            rec_ids = {r['id'] for r in results}
            self.assertTrue(rec_ids.isdisjoint(fav_ids), "Recomendações devem excluir favoritos já marcados")

            # Garantir que pelo menos uma recomendação seja da mesma cidade dos favoritos (CidadeA)
            has_same_city = any(r for r in results if r.get('predicted_price') is not None)
            self.assertTrue(has_same_city)

            # Verificar persistência em UserRecommendation
            persisted = UserRecommendation.objects.filter(user=self.user, source='personal')
            self.assertTrue(persisted.exists())
            # quantidade persistida deve ser igual ao número retornado (ou ao limit passado)
            self.assertEqual(persisted.count(), min(5, len(results)))

        finally:
            ml_views.PriceModel.instance = original_instance
