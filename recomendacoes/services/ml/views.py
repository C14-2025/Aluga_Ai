from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import PriceInputSerializer, PriceOutputSerializer
from .services.model import PriceModel

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
        out = PriceOutputSerializer({
            "predicted_price": float(pred),
            "method": method,
            "details": {k: float(v) for k, v in (details or {}).items()}
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
