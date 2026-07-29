from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from EcomApp.models import Product, Store, StoreProduct, Review, Wishlist
from EcomApp.serializers import ProductSerializer, ReviewSerializer, WishlistSerializer
from EcomApp.customjwtauthentication import CustomJWTAuthentication

class CustomProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomProductPagination

    def perform_create(self, serializer):
        product = serializer.save()
        if self.request.user.is_authenticated:
            store = Store.objects.filter(owner=self.request.user).first()
            if store:
                StoreProduct.objects.create(store=store, product=product)

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images').all()
        category_name = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        search_query = self.request.query_params.get('search')
        store_id = self.request.query_params.get('store_id')

        if store_id:
            queryset = queryset.filter(storeproduct__store__store_id=store_id)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        if category_name and category_name.lower() != 'all objects':
            queryset = queryset.filter(category__name__iexact=category_name)
        if min_price not in (None, ''):
            queryset = queryset.filter(price__gte=min_price)
        if max_price not in (None, ''):
            queryset = queryset.filter(price__lte=max_price)

        return queryset.order_by('id')

class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.select_related('category').prefetch_related('images').all()
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

class ReviewView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        try:
            product = Product.objects.get(product_id=product_id)
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )
            return Response({'message': 'Review submitted successfully'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request):
        try:
            product = Product.objects.get(product_id=request.data.get("product_id"))
            reviews = Review.objects.filter(product=product)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request):
        review_id = request.data.get('review_id')
        try:
            review = Review.objects.get(id=review_id, user=request.user)
            review.delete()
            return Response({'message': 'Review deleted successfully'}, status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({'error': 'Review does not exist'}, status=status.HTTP_404_NOT_FOUND)

class WishlistView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(product_id=product_id)
            Wishlist.objects.create(user=request.user, product=product)
            return Response({'message': 'Product added to wishlist'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(product_id=product_id)
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                return Response({'message': 'Product removed from wishlist'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Product not found in wishlist'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
