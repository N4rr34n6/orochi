from django.contrib.sites.models import Site
from django.conf import settings
from rest_framework import serializers
from orochi.website.models import Dump, Result, Plugin, ExtractedDump, OPERATING_SYSTEM
from orochi.users.api.serializers import ShortUserSerializer
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer


class ExtractedDumpSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    def get_path(self, obj):
        path = Site.objects.get_current().domain
        return "http://{}{}".format(
            path, obj.path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL.rstrip("/"))
        )

    class Meta:
        model = ExtractedDump
        read_only_fields = ("sha256",)
        fields = ["path", "sha256", "clamav", "vt_report", "reg_array"]


class ShortExtractedDumpSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {"dump_pk": "result__dump__pk", "result_pk": "result__pk"}

    class Meta:
        model = ExtractedDump
        fields = ["sha256", "pk", "url"]
        extra_kwargs = {
            "url": {"view_name": "api:dump-plugins-ext-detail", "lookup_field": "pk"}
        }


class PluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = [
            "name",
            "operating_system",
            "disabled",
            "local_dump",
            "vt_check",
            "clamav_check",
            "regipy_check",
            "url",
        ]

        extra_kwargs = {"url": {"view_name": "api:plugin-detail", "lookup_field": "pk"}}


class ShortPluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = [
            "name",
            "operating_system",
            "disabled",
            "pk",
            "url",
        ]

        extra_kwargs = {"url": {"view_name": "api:plugin-detail", "lookup_field": "pk"}}


class ResultSerializer(serializers.ModelSerializer):
    plugin = ShortPluginSerializer(many=False, read_only=True)
    result = serializers.SerializerMethodField()
    extracted_dumps = ShortExtractedDumpSerializer(
        many=True, read_only=True, source="extracteddump_set"
    )

    def get_result(self, obj):
        return obj.get_result_display()

    class Meta:
        model = Result
        read_only_fields = ("description",)
        fields = [
            "plugin",
            "result",
            "description",
            "parameter",
            "updated_at",
            "extracted_dumps",
        ]


class ShortResultSerializer(NestedHyperlinkedModelSerializer):
    plugin = serializers.StringRelatedField(many=False)
    result = serializers.SerializerMethodField()

    parent_lookup_kwargs = {"dump_pk": "dump__pk"}

    def get_result(self, obj):
        return obj.get_result_display()

    class Meta:
        model = Result
        fields = ["plugin", "result", "pk", "url"]
        extra_kwargs = {"url": {"view_name": "api:dump-plugins-detail"}}


class DumpSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    author = ShortUserSerializer(many=False, read_only=True)
    index = serializers.ReadOnlyField()
    upload = serializers.FileField(allow_empty_file=False)
    plugins = ShortResultSerializer(
        many=True, read_only=True, source="plugins.through.objects"
    )

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Dump
        fields = [
            "operating_system",
            "name",
            "index",
            "author",
            "created_at",
            "status",
            "upload",
            "plugins",
        ]

        extra_kwargs = {
            "upload": {"write_only": True},
        }


class ShortDumpSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    author = ShortUserSerializer(many=False, read_only=True)

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Dump
        fields = [
            "operating_system",
            "author",
            "name",
            "created_at",
            "status",
            "pk",
            "url",
        ]

        extra_kwargs = {
            "url": {"view_name": "api:dump-detail", "lookup_field": "pk"},
        }
