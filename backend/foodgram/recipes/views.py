from io import BytesIO

from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from users.models import User

from .models import Amount, Favorite, Follow, Ingredient, Recipe, Tag
from .pagination import CustomPagination
from .permissions import (IngredientPermission, IsAuthenticatedPermission,
                          RecipePermission)
from .serializers import (AmountSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingSerializer, TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IngredientPermission]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [RecipePermission]
    pagination_class = CustomPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FollowersViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedPermission]

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)


@api_view(['GET', 'DELETE'])
def hello(request, pk):
    if request.method == 'GET':
        data = Follow.objects.get_or_create(
            user=User(id=request.user.id),
            following=User(id=pk)
        )
        results = FollowSerializer(data[0]).data
        return Response(results)
    if request.method == 'DELETE':
        follow_to_delete = Follow.objects.get(
            user=User(id=request.user.id),
            following=User(id=pk)
        )
        follow_to_delete.delete()
        return Response({'message': "Вы отписались от пользователя!"})
    return False


@api_view(['GET', 'DELETE'])
def favorite(request, pk):
    if request.method == 'GET':
        Favorite.objects.create(
            user=User(id=request.user.id),
            recipe=Recipe(id=pk)
        )
        data = Favorite.objects.get(
            user=User(id=request.user.id),
            recipe=Recipe(id=pk)
        )
        results = FavoriteSerializer(data).data
        return Response(results)
    if request.method == 'DELETE':
        favorite_to_delete = Favorite.objects.get(
            user=User(id=request.user.id),
            recipe=Recipe(id=pk)
        )
        favorite_to_delete.delete()
        return Response({'message': "Рецепт удален из избранного!"})
    return False


class ShoppingListViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def shopping_cart_add(self, request, pk):
        recipe_to_add = Recipe.objects.get(
            id=pk
        )
        recipe_to_add.is_in_shopping_cart = True
        recipe_to_add.save()
        results = ShoppingSerializer(recipe_to_add).data
        return Response(results)

    @action(detail=False, methods=['delete'])
    def shopping_cart_del(self, request, pk):
        recipe_to_del = Recipe.objects.get(
                id=pk
        )
        recipe_to_del.is_in_shopping_cart = False
        recipe_to_del.save()
        return Response({'message': "Рецепт удален из списка покупок!"})

    @action(detail=False, methods=['get'])
    def download_shopping_list(self, request):
        queryset = Amount.objects.filter(recipe__is_in_shopping_cart=True)
        serializer = AmountSerializer(queryset, many=True)
        shopping_list = {}
        for i in serializer.data:
            if i["name"] not in shopping_list:
                shopping_list[i["name"]] = (i["amount"], i["measurement_unit"])
            else:
                rez = shopping_list[i["name"]][0] + i["amount"]
                shopping_list[i["name"]] = (rez, i["measurement_unit"])

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="somefilename.pdf"')

        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        fname = 'a010013l'
        facename = 'URWGothicL-Book'
        cyrface = pdfmetrics.EmbeddedType1Face(fname+'.afm', fname+'.pfb')
        cyrenc = pdfmetrics.Encoding('CP1251')

        cp1251 = (
               'afii10051', 'afii10052', 'quotesinglbase', 'afii10100',
               'quotedblbase', 'ellipsis', 'dagger', 'daggerdbl', 'Euro',
               'perthousand', 'afii10058', 'guilsinglleft', 'afii10059',
               'afii10061', 'afii10060', 'afii10145', 'afii10099', 'quoteleft',
               'quoteright', 'quotedblleft', 'quotedblright', 'bullet',
               'endash', 'emdash', 'tilde', 'trademark', 'afii10106',
               'guilsinglright', 'afii10107', 'afii10109', 'afii10108',
               'afii10193', 'space', 'afii10062', 'afii10110', 'afii10057',
               'currency', 'afii10050', 'brokenbar', 'section', 'afii10023',
               'copyright', 'afii10053', 'guillemotleft', 'logicalnot',
               'hyphen', 'registered', 'afii10056', 'degree', 'plusminus',
               'afii10055', 'afii10103', 'afii10098', 'mu1', 'paragraph',
               'periodcentered',
               'afii10071', 'afii61352', 'afii10101', 'guillemotright',
               'afii10105', 'afii10054', 'afii10102', 'afii10104',
               'afii10017', 'afii10018', 'afii10019', 'afii10020', 'afii10021',
               'afii10022', 'afii10024', 'afii10025', 'afii10026', 'afii10027',
               'afii10028', 'afii10029', 'afii10030', 'afii10031', 'afii10032',
               'afii10033', 'afii10034', 'afii10035', 'afii10036', 'afii10037',
               'afii10038', 'afii10039', 'afii10040', 'afii10041', 'afii10042',
               'afii10043', 'afii10044', 'afii10045', 'afii10046', 'afii10047',
               'afii10048', 'afii10049', 'afii10065', 'afii10066', 'afii10067',
               'afii10068', 'afii10069', 'afii10070', 'afii10072', 'afii10073',
               'afii10074', 'afii10075', 'afii10076', 'afii10077', 'afii10078',
               'afii10079', 'afii10080', 'afii10081', 'afii10082', 'afii10083',
               'afii10084', 'afii10085', 'afii10086', 'afii10087', 'afii10088',
               'afii10089', 'afii10090', 'afii10091', 'afii10092', 'afii10093',
               'afii10094', 'afii10095', 'afii10096', 'afii10097'
        )

        for i in range(128, 256):
            cyrenc[i] = cp1251[i-128]

        pdfmetrics.registerEncoding(cyrenc)
        pdfmetrics.registerTypeFace(cyrface)
        pdfmetrics.registerFont(
            pdfmetrics.Font(facename+'1251', facename, 'CP1251'))
        c.setFont(facename+'1251', 20)

        counter = 0
        y_coord = 780
        c.drawString(25, 800, "Список покупок:")
        for i in shopping_list:
            counter += 1
            y_coord -= 30
            string = (str(counter) + '. ' + i + ' - ' +
                      str(shopping_list[i][0]) + ' ' + shopping_list[i][1])

            c.drawString(25, y_coord, string)
        c.showPage()
        c.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
