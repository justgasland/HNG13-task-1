from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import String
from .serializers import StringSerializer
from .utils import analyze_string, parse_natural_language_query


class StringListCreateView(APIView):
   

    def get(self, request):
        queryset = String.objects.all()
        filters_applied = {}

        # Filtering logic
        is_palindrome = request.GET.get('is_palindrome')
        if is_palindrome is not None:
            is_palindrome_bool = is_palindrome.lower() == 'true'
            queryset = queryset.filter(is_palindrome=is_palindrome_bool)
            filters_applied['is_palindrome'] = is_palindrome_bool

        min_length = request.GET.get('min_length')
        if min_length:
            try:
                min_length = int(min_length)
                queryset = queryset.filter(length__gte=min_length)
                filters_applied['min_length'] = min_length
            except ValueError:
                return Response({'error': 'min_length must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        max_length = request.GET.get('max_length')
        if max_length:
            try:
                max_length = int(max_length)
                queryset = queryset.filter(length__lte=max_length)
                filters_applied['max_length'] = max_length
            except ValueError:
                return Response({'error': 'max_length must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        word_count = request.GET.get('word_count')
        if word_count:
            try:
                word_count = int(word_count)
                queryset = queryset.filter(word_count=word_count)
                filters_applied['word_count'] = word_count
            except ValueError:
                return Response({'error': 'word_count must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        contains_character = request.GET.get('contains_character')
        if contains_character:
            if len(contains_character) != 1:
                return Response({'error': 'contains_character must be a single character'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(value__icontains=contains_character)
            filters_applied['contains_character'] = contains_character

        serializer = StringSerializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'count': queryset.count(),
            'filters_applied': filters_applied
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if 'value' not in request.data:
            return Response({'error': 'Missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)

        value = request.data.get('value')
        if not isinstance(value, str):
            return Response({'error': 'Invalid data type for "value". Must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Analyze the string
        properties = analyze_string(value)

        # Check duplicate
        if String.objects.filter(sha256_hash=properties['sha256_hash']).exists():
            return Response({'error': 'String already exists in the system'}, status=status.HTTP_409_CONFLICT)

        # Save new string
        string_obj = String.objects.create(
            value=value,
            length=properties['length'],
            is_palindrome=properties['is_palindrome'],
            unique_characters=properties['unique_characters'],
            word_count=properties['word_count'],
            sha256_hash=properties['sha256_hash'],
            char_frequency=properties['char_frequency']
        )

        serializer = StringSerializer(string_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StringDetailView(APIView):
    

    def get(self, request, string_value):
        string_obj = get_object_or_404(String, value=string_value)
        serializer = StringSerializer(string_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, string_value):
        string_obj = get_object_or_404(String, value=string_value)
        string_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FilterByNaturalLanguageView(APIView):
    
    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return Response({'error': 'Missing "query" parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed_filters = parse_natural_language_query(query)
        except Exception as e:
            return Response({'error': f'Unable to parse natural language query: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = String.objects.all()

        if 'is_palindrome' in parsed_filters:
            queryset = queryset.filter(is_palindrome=parsed_filters['is_palindrome'])
        if 'word_count' in parsed_filters:
            queryset = queryset.filter(word_count=parsed_filters['word_count'])
        if 'min_length' in parsed_filters:
            queryset = queryset.filter(length__gte=parsed_filters['min_length'])
        if 'max_length' in parsed_filters:
            queryset = queryset.filter(length__lte=parsed_filters['max_length'])
        if 'contains_character' in parsed_filters:
            queryset = queryset.filter(value__icontains=parsed_filters['contains_character'])

        serializer = StringSerializer(queryset, many=True)
        return Response({
            'data': serializer.data,
            'count': queryset.count(),
            'interpreted_query': {
                'original': query,
                'parsed_filters': parsed_filters
            }
        }, status=status.HTTP_200_OK)
