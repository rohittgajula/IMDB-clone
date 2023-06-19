from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
# from rest_framework import mixins

from .permissions import IsAdminOrReadonly, IsReviewUserOrReadOnly

from .models import WatchList as watchlist
from .models import StreamPlatform as streamplatform
from .models import Review
from .serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer

# ---------------------CONCRETE VIEW CLASS (only generic views)-------------------------------

# using only generic API views | Concrete view class
class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()           # this returns all the objects(reviews)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):         # this filter object according to the movie.
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):  # get, put, delete
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]          # from permissions.py

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):    # provides overring | Save and deletion hooks | concrete class views
        pk = self.kwargs.get('pk')           # also have perform_update perform_destroy
        watchlist_movie = watchlist.objects.get(pk=pk)

        review_user = self.request.user        # we are getting current user 
        review_queryset = Review.objects.filter(watchlist=watchlist_movie, review_user=review_user)

        watch = watchlist.objects.get(pk=pk)    # WITHOUT THIS YOU WILL GET "DeferredAttribute."

        if review_queryset.exists():        
            raise ValidationError('You have already reviewed this movie.')
        
        if watch.number_ratings == 0:
                                    # here providing validated data from serializers
            watch.avg_rating = serializer.validated_data['rating']
        else:
                                    # (old rating + new rating) / 2
            watch.avg_rating = (int(watch.avg_rating) + serializer.validated_data['rating']) / 2

        # for number of ratings == current ratings + one.
        watch.number_ratings = watch.number_ratings + 1
        watch.save()

        serializer.save(watchlist = watchlist_movie, review_user = review_user)

# -----------------------GENERIC VIEW & MIXINS (generic views & mixins)--------------------------

# using mixins
# we can perform get, post, put, delete op. | Generic views & mixins
# using generic view sets and mixins.
# class ReviewList(mixins.ListModelMixin,
#                  mixins.CreateModelMixin,
#                  generics.GenericAPIView):
    
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)      # list for many items.

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
    
# # retrive one data using generic views | using mixins & generic views
# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)  # retrive for single item.
    
# ---------------------------------------------------------------------------------------

# ----------------------------Using APIview sets----------------------------------------
class WatchList(APIView):
    permission_classes = [IsAdminOrReadonly]            # imported from permission.py

    def get(self, request):
        movies = watchlist.objects.all()
        serializer = WatchListSerializer(movies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        serializer = WatchListSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors ,status.HTTP_404_NOT_FOUND)

class WatchListDetail(APIView):
    permission_classes = [IsAdminOrReadonly]          # imported from permission.py

    def get(self, request, pk):
        try:
            movie = watchlist.objects.get(pk=pk)
        except watchlist.DoesNotExist:
            return Response({'error':'item not found'}, status.HTTP_404_NOT_FOUND)
        serializer = WatchListSerializer(movie)
        return Response(serializer.data)
    
    def put(self, request, pk):
        data = request.data
        movie = watchlist.objects.get(pk=pk)
        serializer = WatchListSerializer(movie, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk):
        movie = watchlist.objects.get(pk=pk)
        movie.delete()
        return Response('Deleted Sucessfully.', status.HTTP_204_NO_CONTENT)
    
# ---------------------------MODEL VIEWSET----------------------------------------
#  model viewset can perform all opperations | Model view sets

# this three lines does all the operations. 
# if you want to only read use ReadOnlyModelViewset in place of ModelViewset
class StreamPlatformMVS(viewsets.ModelViewSet):
    queryset = streamplatform.objects.all()
    serializer_class = StreamPlatformSerializer
    
# ----------------------------VIEW SETS-----------------------------------------
# viewswts helps to decrease code or write all operations in one class

class StreamPlatformVS(viewsets.ViewSet):

    def list(self, request):
        queryset = streamplatform.objects.all()
        serializer = StreamPlatformSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrive(self, request, pk=None):
        queryset = streamplatform.objects.all()
        watchlist = get_object_or_404(queryset, pk=pk)
        serializer = StreamPlatformSerializer(watchlist)
        return Response(serializer.data)
    
    def create(self, request):
        data = request.data
        serializer = StreamPlatformSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

# ----------------------------------||-------------------------------------------
    
class StreamPlatform(APIView):
    permission_classes = [IsAdminOrReadonly]            # imported from permission.py

    def get(self, request):
        platform = streamplatform.objects.all()
        serializer = StreamPlatformSerializer(platform, many=True)  # context = {'request':request}
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        serializer = StreamPlatformSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_404_NOT_FOUND)
        
class StreamPlatformDetail(APIView):
    permission_classes = [IsAdminOrReadonly]            # imported from permission.py

    def get(self, request, pk):
        platform = streamplatform.objects.get(pk=pk)
        serializer = StreamPlatformSerializer(platform)  # context={'request': request}
        return Response(serializer.data)
    
    def put(self, request, pk):
        data = request.data
        platform = streamplatform.objects.get(pk=pk)
        serializer = StreamPlatformSerializer(platform, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors ,status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk):
        platform = streamplatform.objects.get(pk=pk)
        platform.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    
# --------------------------------------------------------
