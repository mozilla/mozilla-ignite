# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'JudgingAnswer'
        db.create_table('challenges_judginganswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('judgement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['challenges.Judgement'])),
            ('criterion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenges.JudgingCriterion'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('challenges', ['JudgingAnswer'])

        # Adding unique constraint on 'JudgingAnswer', fields ['judgement', 'criterion']
        db.create_unique('challenges_judginganswer', ['judgement_id', 'criterion_id'])

        # Adding model 'Judgement'
        db.create_table('challenges_judgement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenges.Submission'])),
            ('judge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Profile'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('challenges', ['Judgement'])

        # Adding unique constraint on 'Judgement', fields ['submission', 'judge']
        db.create_unique('challenges_judgement', ['submission_id', 'judge_id'])

        # Adding model 'JudgingCriterion'
        db.create_table('challenges_judgingcriterion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250)),
            ('min_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_value', self.gf('django.db.models.fields.IntegerField')(default=10)),
        ))
        db.send_create_signal('challenges', ['JudgingCriterion'])

        # Adding M2M table for field phases on 'JudgingCriterion'
        db.create_table('challenges_judgingcriterion_phases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('judgingcriterion', models.ForeignKey(orm['challenges.judgingcriterion'], null=False)),
            ('phase', models.ForeignKey(orm['challenges.phase'], null=False))
        ))
        db.create_unique('challenges_judgingcriterion_phases', ['judgingcriterion_id', 'phase_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Judgement', fields ['submission', 'judge']
        db.delete_unique('challenges_judgement', ['submission_id', 'judge_id'])

        # Removing unique constraint on 'JudgingAnswer', fields ['judgement', 'criterion']
        db.delete_unique('challenges_judginganswer', ['judgement_id', 'criterion_id'])

        # Deleting model 'JudgingAnswer'
        db.delete_table('challenges_judginganswer')

        # Deleting model 'Judgement'
        db.delete_table('challenges_judgement')

        # Deleting model 'JudgingCriterion'
        db.delete_table('challenges_judgingcriterion')

        # Removing M2M table for field phases on 'JudgingCriterion'
        db.delete_table('challenges_judgingcriterion_phases')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'challenges.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        },
        'challenges.challenge': {
            'Meta': {'object_name': 'Challenge'},
            'allow_voting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'moderate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        'challenges.externallink': {
            'Meta': {'object_name': 'ExternalLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenges.Submission']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        },
        'challenges.judgement': {
            'Meta': {'unique_together': "(('submission', 'judge'),)", 'object_name': 'Judgement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'judge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Profile']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenges.Submission']"})
        },
        'challenges.judginganswer': {
            'Meta': {'unique_together': "(('judgement', 'criterion'),)", 'object_name': 'JudgingAnswer'},
            'criterion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenges.JudgingCriterion']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'judgement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['challenges.Judgement']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {})
        },
        'challenges.judgingcriterion': {
            'Meta': {'object_name': 'JudgingCriterion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_value': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'min_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'phases': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'judgement_criteria'", 'blank': 'True', 'to': "orm['challenges.Phase']"}),
            'question': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'})
        },
        'challenges.phase': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('challenge', 'name'),)", 'object_name': 'Phase'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'phases'", 'to': "orm['challenges.Challenge']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 17, 9, 52, 45, 555474)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 17, 9, 52, 45, 555425)'})
        },
        'challenges.submission': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Submission'},
            'brief_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenges.Category']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Profile']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 1, 17, 17, 52, 45, 558673)'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'flagged_offensive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'flagged_offensive_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_live': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_winner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['challenges.Phase']"}),
            'sketh_note': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'allow_participation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_sub_projects': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects_following'", 'symmetrical': 'False', 'to': "orm['users.Profile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent_project_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'sub_project_label': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'team_members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Profile']", 'symmetrical': 'False'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['topics.Topic']", 'symmetrical': 'False'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        },
        'topics.topic': {
            'Meta': {'object_name': 'Topic'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'draft': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'users.profile': {
            'Meta': {'object_name': 'Profile'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['challenges']
