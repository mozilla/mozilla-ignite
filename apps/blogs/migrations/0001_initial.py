# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BlogEntry'
        db.create_table('blogs_blogentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('summary', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('checksum', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('autor', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('blogs', ['BlogEntry'])


    def backwards(self, orm):
        
        # Deleting model 'BlogEntry'
        db.delete_table('blogs_blogentry')


    models = {
        'blogs.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'autor': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'checksum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['blogs']
