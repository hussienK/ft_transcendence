# Generated by Django 4.2.16 on 2024-12-25 16:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentparticipant',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tournamentmatch',
            name='game_session',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_match', to='game.gamesession'),
        ),
        migrations.AddField(
            model_name='tournamentmatch',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='game.tournament'),
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='forfeited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forfeited_matches', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='game_session',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='match_history', to='game.gamesession'),
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player1_match_history', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='matchhistory',
            name='player2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player2_match_history', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='player1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player1_sessions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='player2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player2_sessions', to=settings.AUTH_USER_MODEL),
        ),
    ]
