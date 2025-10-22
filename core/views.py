from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer, StringInputSerializer
from .utils import analyze_string, parse_natural_language_query


class StringCreateListView(APIView):
    """
    POST /strings - Create and analyze a new string
    GET /strings - List all strings with optional filtering
    """
    
    def post(self, request):
        """
        Create and analyze a new string
        
        Returns:
            201: String created successfully
            400: Invalid request body or missing "value" field
            409: String already exists
            422: Invalid data type for "value"
        """
        # Validate input
        input_serializer = StringInputSerializer(data=request.data)
        
        # Check if 'value' field exists
        if 'value' not in request.data:
            return Response(
                {'error': 'Missing "value" field in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate data type
        if not input_serializer.is_valid():
            # Check if it's a type error
            value = request.data.get('value')
            if not isinstance(value, str):
                return Response(
                    {'error': 'Invalid data type for "value". Must be a string.'},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            return Response(
                {'error': 'Invalid request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        value = input_serializer.validated_data['value']
        
        # Analyze the string
        properties = analyze_string(value)
        
        # Check if string already exists (by sha256_hash)
        if AnalyzedString.objects.filter(sha256_hash=properties['sha256_hash']).exists():
            return Response(
                {'error': 'String already exists in the system'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create new AnalyzedString object
        analyzed_string = AnalyzedString.objects.create(
            value=properties['value'],
            sha256_hash=properties['sha256_hash'],
            length=properties['length'],
            is_palindrome=properties['is_palindrome'],
            unique_characters=properties['unique_characters'],
            word_count=properties['word_count'],
            character_frequency_map=properties['character_frequency_map']
        )
        
        # Serialize and return
        serializer = AnalyzedStringSerializer(analyzed_string)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        """
        List all strings with optional filtering
        
        Query Parameters:
            is_palindrome: boolean (true/false)
            min_length: integer (minimum string length)
            max_length: integer (maximum string length)
            word_count: integer (exact word count)
            contains_character: string (single character to search for)
        
        Returns:
            200: List of strings with filters applied
            400: Invalid query parameter values or types
        """
        queryset = AnalyzedString.objects.all()
        filters_applied = {}
        
        # Apply filters from query parameters
        try:
            # Filter by is_palindrome
            is_palindrome = request.GET.get('is_palindrome')
            if is_palindrome is not None:
                if is_palindrome.lower() not in ['true', 'false']:
                    return Response(
                        {'error': 'Invalid value for is_palindrome. Must be true or false.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                is_palindrome_bool = is_palindrome.lower() == 'true'
                queryset = queryset.filter(is_palindrome=is_palindrome_bool)
                filters_applied['is_palindrome'] = is_palindrome_bool
            
            # Filter by min_length
            min_length = request.GET.get('min_length')
            if min_length is not None:
                try:
                    min_length_int = int(min_length)
                    if min_length_int < 0:
                        raise ValueError("min_length must be non-negative")
                    queryset = queryset.filter(length__gte=min_length_int)
                    filters_applied['min_length'] = min_length_int
                except ValueError:
                    return Response(
                        {'error': 'Invalid value for min_length. Must be a valid integer.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Filter by max_length
            max_length = request.GET.get('max_length')
            if max_length is not None:
                try:
                    max_length_int = int(max_length)
                    if max_length_int < 0:
                        raise ValueError("max_length must be non-negative")
                    queryset = queryset.filter(length__lte=max_length_int)
                    filters_applied['max_length'] = max_length_int
                except ValueError:
                    return Response(
                        {'error': 'Invalid value for max_length. Must be a valid integer.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Filter by word_count
            word_count = request.GET.get('word_count')
            if word_count is not None:
                try:
                    word_count_int = int(word_count)
                    if word_count_int < 0:
                        raise ValueError("word_count must be non-negative")
                    queryset = queryset.filter(word_count=word_count_int)
                    filters_applied['word_count'] = word_count_int
                except ValueError:
                    return Response(
                        {'error': 'Invalid value for word_count. Must be a valid integer.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Filter by contains_character
            contains_character = request.GET.get('contains_character')
            if contains_character is not None:
                if len(contains_character) != 1:
                    return Response(
                        {'error': 'contains_character must be a single character'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                queryset = queryset.filter(value__icontains=contains_character)
                filters_applied['contains_character'] = contains_character
        
        except Exception as e:
            return Response(
                {'error': f'Invalid query parameters: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize results
        serializer = AnalyzedStringSerializer(queryset, many=True)
        
        return Response({
            'data': serializer.data,
            'count': queryset.count(),
            'filters_applied': filters_applied
        }, status=status.HTTP_200_OK)


class StringDetailView(APIView):
    """
    GET /strings/{string_value} - Get a specific string
    DELETE /strings/{string_value} - Delete a specific string
    """
    
    def get(self, request, string_value):
        """
        Get a specific string by its value
        
        Returns:
            200: String found and returned
            404: String does not exist
        """
        try:
            analyzed_string = AnalyzedString.objects.get(value=string_value)
            serializer = AnalyzedStringSerializer(analyzed_string)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AnalyzedString.DoesNotExist:
            return Response(
                {'error': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, string_value):
        """
        Delete a specific string by its value
        
        Returns:
            204: String deleted successfully (no content)
            404: String does not exist
        """
        try:
            analyzed_string = AnalyzedString.objects.get(value=string_value)
            analyzed_string.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AnalyzedString.DoesNotExist:
            return Response(
                {'error': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )


class NaturalLanguageFilterView(APIView):
    """
    GET /strings/filter-by-natural-language - Filter strings using natural language
    """
    
    def get(self, request):
        """
        Filter strings using natural language query
        
        Query Parameters:
            query: Natural language query string
        
        Returns:
            200: Filtered results with interpreted query
            400: Unable to parse query
            422: Query parsed but resulted in conflicting filters
        """
        query = request.GET.get('query')
        
        # Validate query parameter exists
        if not query:
            return Response(
                {'error': 'Missing "query" parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse the natural language query
        try:
            parsed_filters = parse_natural_language_query(query)
        except ValueError as e:
            # Check if it's a conflict error
            if 'conflicting' in str(e).lower():
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            # Otherwise it's a parsing error
            return Response(
                {'error': f'Unable to parse natural language query: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build queryset based on parsed filters
        queryset = AnalyzedString.objects.all()
        
        try:
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
        
        except Exception as e:
            return Response(
                {'error': f'Error applying filters: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize results
        serializer = AnalyzedStringSerializer(queryset, many=True)
        
        return Response({
            'data': serializer.data,
            'count': queryset.count(),
            'interpreted_query': {
                'original': query,
                'parsed_filters': parsed_filters
            }
        }, status=status.HTTP_200_OK)