from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Evaluation
from .models import EvaluationRate
from .models import Question
from .models import Option
from .models import EvaluationRecord
from .models import EvaluationDetail
from .models import Story

from .serializers import EvaluationSerializer
from .serializers import EvaluationRateSerializer
from .serializers import QuestionSerializer
from .serializers import OptionSerializer
from .serializers import EvaluationRecordSerializer
from .serializers import EvaluationDetailSerializer
from .serializers import StorySerializer

from datetime import datetime



# Create your views here.
class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

    @action(methods=['get'], detail=True)
    def details(self, request, pk=None):
        if pk == None:
            return Response(status=404)
        evaqueryset = Evaluation.objects.get(id=pk)
        evaluation = EvaluationSerializer(evaqueryset, many=False)
        quesqueryset = Question.objects.filter(evaluation_id=pk)
        question = QuestionSerializer(quesqueryset, many=True)
        questiondata = question.data
        for temp in questiondata:
            optionqueryset = Option.objects.filter(question_id=temp['id'])
            option = OptionSerializer(optionqueryset, many=True)
            temp['options'] = option.data
        res = dict(evaluation.data)
        res['questions'] = questiondata
        return Response(res)

    @action(methods=['post'], detail=False)
    def score(self, request, pk=None):
        requestdata = request.data
        scoresum = 0
        optionqueryset = Option.objects.filter(pk__in=requestdata['options'])
        optiondata = OptionSerializer(optionqueryset, many=True).data
        for temp in optiondata:
            scoresum += temp['score']
        # user 临时为none
        user = None
        ftime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3]
        evaluationrecord = EvaluationRecord(user=user, score=scoresum, timestamp=ftime)
        evaluationrecord.evaluation = Evaluation.objects.get(id=requestdata['evaluation'])
        evaluationrecord.save()
        recqueryset = EvaluationRecord.objects.filter(user=user, evaluation=requestdata['evaluation'], timestamp=ftime)
        rec_id = EvaluationRecordSerializer(recqueryset, many=True).data[0]['id']
        savaid = {'id': rec_id}

        data = zip(requestdata['question'], requestdata['options'])
        for i, j in data:
            detail_data = EvaluationDetail()
            detail_data.option = Option.objects.get(id=j)
            detail_data.evaluation = evaluationrecord
            detail_data.question = Question.objects.get(id=i)
            detail_data.save()

        return Response(savaid)


class EvaluationRateViewSet(viewsets.ModelViewSet):
    queryset = EvaluationRate.objects.all()
    serializer_class = EvaluationRateSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class EvaluationRecordViewSet(viewsets.ModelViewSet):
    queryset = EvaluationRecord.objects.all()
    serializer_class = EvaluationRecordSerializer

    @action(methods=['get'], detail=True)
    def details(self, request, pk=None):
        evaratequeryset = EvaluationRate.objects.get(id='1')
        return Response(EvaluationRateSerializer(evaratequeryset, many=False).data)


class EvaluationDetailViewSet(viewsets.ModelViewSet):
    queryset = EvaluationDetail.objects.all()
    serializer_class = EvaluationDetailSerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    @action(methods=['post'], detail=False)
    def recommend(self, request, pk=None):
        requestdata = request.data
        evaluationRecordId = requestdata['id']
        evaluationRecord = EvaluationRecord.objects.get(id=evaluationRecordId)
        score = evaluationRecord.score
        # evaluation = evaluationRecord.evaluation
        # evaluationRate = EvaluationRecord.objects.filter(evaluation=evaluation)
        # recqueryset = EvaluationRecordSerializer(evaluationRate, many=True).data
        data = {'level': 1, 'title':'title1', 'url':'url1', 'type':'type1' }
        return Response(data)

