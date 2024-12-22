from .models import Tournament, TournamentParticipant
from rest_framework import serializers

class TournamentParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentParticipant
        fields = ['id', 'user', 'alias']

class TournamentSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'created_at', 'is_active', 'participants']

    def get_participants(self, obj):
        participants = TournamentParticipant.objects.filter(tournament=obj)
        return [
            {
                'id': participant.user.id,
                'username': participant.user.username,
                'joined_at': participant.joined_at,
            }
            for participant in participants
        ]