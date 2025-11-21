from rest_framework import serializers

class PriceInputSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['Casa', 'Apartamento'])
    cidade = serializers.CharField()
    area_m2 = serializers.FloatField(min_value=10)
    quartos = serializers.IntegerField(min_value=0)
    banheiros = serializers.IntegerField(min_value=0)
    vagas_garagem = serializers.IntegerField(min_value=0)
    # campos extras do JSON (ignorados pelo modelo, mas aceitos para evolução futura)
    bairro = serializers.CharField(required=False, allow_blank=True)
    condominio = serializers.FloatField(required=False, min_value=0)
    iptu = serializers.FloatField(required=False, min_value=0)

class PriceOutputSerializer(serializers.Serializer):
    predicted_price = serializers.FloatField()
    method = serializers.CharField()
    details = serializers.DictField(child=serializers.FloatField(), required=False)

class CandidateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    city = serializers.CharField()
    neighborhood = serializers.CharField(allow_blank=True, required=False)
    area = serializers.FloatField()
    bedrooms = serializers.IntegerField()
    bathrooms = serializers.IntegerField()
    parking = serializers.IntegerField()
    property_type = serializers.ChoiceField(choices=['apartment', 'studio', 'house', 'kitnet'])

class RecommendationInputSerializer(serializers.Serializer):
    budget = serializers.FloatField(min_value=100)
    city = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=50, required=False, default=10)
    candidates = CandidateSerializer(many=True, required=False)

class RecommendationOutputItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    city = serializers.CharField()
    predicted_price = serializers.FloatField()
    score = serializers.FloatField()


class SurveyInputSerializer(serializers.Serializer):
    budget = serializers.FloatField(min_value=0)
    city = serializers.CharField(required=False, allow_blank=True)
    property_type = serializers.CharField(required=False, allow_blank=True)
    min_area = serializers.FloatField(required=False, min_value=0)
    max_area = serializers.FloatField(required=False, min_value=0)
    bedrooms = serializers.IntegerField(required=False, min_value=0)
    bathrooms = serializers.IntegerField(required=False, min_value=0)
    parking = serializers.IntegerField(required=False, min_value=0)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=10)
