from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    PriceInputSerializer,
    PriceOutputSerializer,
    RecommendationInputSerializer,
    RecommendationOutputItemSerializer,
)
from .services.model import PriceModel
from .services.recommender import recommend as reco_recommend
from .serializers import SurveyInputSerializer
from rest_framework.permissions import IsAdminUser

class PricePredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PriceInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        model = PriceModel.instance()
        pred, method, details = model.predict(ser.validated_data, return_details=True)
        out = PriceOutputSerializer({
            "predicted_price": float(pred),
            "method": method,
            "details": {k: float(v) for k, v in (details or {}).items()} if details else None
        })
        return Response(out.data, status=status.HTTP_200_OK)

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecommendationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = serializer.validated_data["budget"]
        city = serializer.validated_data.get("city")
        limit = serializer.validated_data.get("limit", 10)
        candidates = serializer.validated_data.get("candidates")

        model = PriceModel.instance()
        items = reco_recommend(model=model, candidates=candidates, budget=budget, city=city, limit=limit)

        out = RecommendationOutputItemSerializer(items, many=True)
        return Response(out.data, status=status.HTTP_200_OK)


class SurveyRecommendationView(APIView):
    """Recebe respostas do usuário (survey) e retorna recomendações.

    Usa o conjunto de candidatos de amostra quando `candidates` não é enviado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = SurveyInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        data = ser.validated_data
        budget = data.get('budget')
        city = data.get('city')
        ptype = data.get('property_type')
        min_area = data.get('min_area')
        max_area = data.get('max_area')
        bedrooms = data.get('bedrooms')
        bathrooms = data.get('bathrooms')
        parking = data.get('parking')
        limit = data.get('limit', 10)

        # carregar candidatos de amostra
        from .services.recommender import _load_sample_candidates
        candidates = _load_sample_candidates()

        # filtrar por preferências do usuário
        def match(c):
            if city and c.get('city', '').lower() != city.lower():
                return False
            if ptype and c.get('property_type', '').lower() != ptype.lower():
                return False
            if min_area and c.get('area', 0) < min_area:
                return False
            if max_area and c.get('area', 0) > max_area:
                return False
            if bedrooms and c.get('bedrooms', 0) < bedrooms:
                return False
            if bathrooms and c.get('bathrooms', 0) < bathrooms:
                return False
            if parking and c.get('parking', 0) < parking:
                return False
            return True

        filtered = [c for c in candidates if match(c)]

        model = PriceModel.instance()
        items = reco_recommend(model=model, candidates=filtered or candidates, budget=budget, city=city, limit=limit)

        out = RecommendationOutputItemSerializer(items, many=True)
        return Response(out.data, status=status.HTTP_200_OK)


class RetrainView(APIView):
    """Endpoint para disparar ETL + treino. Somente staff/admin pode usar."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        # executar ETL e treino síncrono (pode demorar)
        try:
            from dados.etl import ETLPipeline
            from recomendacoes.train_model import ModelTrainer

            pipeline = ETLPipeline()
            out = pipeline.run()

            trainer = ModelTrainer()
            metrics = trainer.train_simple()

            return Response({
                'status': 'ok',
                'etl_output': str(out),
                'metrics': metrics,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
