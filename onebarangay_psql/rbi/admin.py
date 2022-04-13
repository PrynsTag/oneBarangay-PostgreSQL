"""Register your rbi models here."""
from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table

from onebarangay_psql.rbi.models import FamilyMember, HouseRecord
from onebarangay_psql.utils.choice_field import ChoicesField


class HouseRecordResource(resources.ModelResource):
    """House Record Resource for import and export model fields."""

    class Meta:
        """Meta class for HouseRecordResource."""

        model = HouseRecord
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ("house_id",)
        fields = (
            "house_id",
            "created_at",
            "updated_at",
            "date_accomplished",
            "address",
            "family_name",
            "street",
        )
        export_order = (
            "house_id",
            "created_at",
            "updated_at",
            "date_accomplished",
            "address",
            "family_name",
            "street",
        )


class HouseRecordAdmin(ImportExportModelAdmin):
    """House Record Admin Integration for import and export."""

    actions = ["export_rbi_to_pdf"]
    resource_class = HouseRecordResource
    list_display = (
        "house_id",
        "created_at",
        "updated_at",
        "date_accomplished",
        "address",
        "family_name",
        "street",
    )
    list_filter = ("created_at", "updated_at", "date_accomplished")
    search_fields = ("house_id", "family_name", "street")
    ordering = ("-created_at", "-updated_at")
    list_per_page = 25
    list_max_show_all = 1000
    list_select_related = True

    @admin.action(
        permissions=["view"],
        description="Download selected rbi as pdf",
    )
    def export_rbi_to_pdf(self, request, queryset: list[HouseRecord]):
        """Print RBI."""
        for obj in queryset:
            data = [
                [
                    "#",
                    "LAST NAME \n(APELYIDO)",
                    "FIRST NAME",
                    "MIDDLE NAME",
                    "EXT",
                    "PLACE OF BIRTH",
                    "DATE OF BIRTH",
                    "SEX \n(M OR F)",
                    "CIVIL \nSTATUS",
                    "MONTHLY \nINCOME",
                    "REMARKS",
                ],
            ]

            family_object = FamilyMember.objects.filter(house_record_id=obj.house_id)

            for family, index in zip(family_object, range(family_object.count())):
                family_data = list(family.__dict__.values())[3:]
                family_data[9] = family_data[9].strftime("%Y-%m-%d")
                gender_choices = ChoicesField(FamilyMember.CivilStatus.choices)
                data.append(
                    [
                        f"{index + 1}.",
                        family_data[4],
                        family_data[2],
                        family_data[3],
                        family_data[10],
                        family_data[6],
                        family_data[9],
                        family_data[13],
                        gender_choices.to_representation(value=family_data[8]),
                        f"{family_data[11]:,.2f}",
                        family_data[12],
                    ]
                )

            count = family_object.count()
            for _ in range(count, 9):
                data.append([])

            filename = "/tmp/rbi.pdf"

            c = canvas.Canvas(
                filename,
                pagesize=landscape(letter),
                pageCompression=1,
            )
            c.setLineWidth(0.3)
            c.setFont("Helvetica", 12)

            table = Table(
                data,
                rowHeights=1 * cm,
                style=[
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ],
            )
            x = 60
            y = (landscape(letter)[1] / 2) - 200
            table.wrapOn(c, 100, 100)
            table.drawOn(c, x, y)

            c.drawString(655, 505, str(obj.house_id))
            c.drawString(125, 415, str(obj.address).replace("\n", " "))
            c.drawString(660, 440, str(obj.date_accomplished.date()))

            c.drawString(400, 20, f"Date Created: {datetime.now().date()}")
            c.drawString(600, 20, f"Date Updated: {obj.updated_at.date()}")

            c.showPage()
            c.save()

            with open("onebarangay_psql/static/pdf/rbi_form.pdf", "rb") as pdf:
                existing_pdf = PdfFileReader(pdf)
                page = existing_pdf.getPage(0)

                new_pdf = PdfFileReader(filename)
                page.mergePage(new_pdf.getPage(0))

                output = PdfFileWriter()
                output.addPage(page)

                with open(filename, "wb") as f:
                    output.write(f)

            with open(filename, "rb") as pdf:
                response = HttpResponse(pdf.read(), content_type="application/pdf")
                response["Content-Disposition"] = "attachment; filename=rbi.pdf"
                return response


class FamilyRecordResource(resources.ModelResource):
    """Family Record Resource for import and export model fields."""

    class Meta:
        """Meta class for FamilyRecordResource."""

        model = FamilyMember
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ("family_member_id",)
        fields = (
            "family_member_id",
            "created_at",
            "updated_at",
            "first_name",
            "middle_name",
            "last_name",
            "age",
            "birth_place",
            "citizenship",
            "civil_status",
            "date_of_birth",
            "monthly_income",
            "remarks",
            "gender",
        )
        export_order = (
            "family_member_id",
            "created_at",
            "updated_at",
            "first_name",
            "middle_name",
            "last_name",
            "age",
            "birth_place",
            "citizenship",
            "civil_status",
            "date_of_birth",
            "monthly_income",
            "remarks",
            "gender",
        )


class FamilyRecordAdmin(ImportExportModelAdmin):
    """Family Record Admin Custom Configuration."""

    resource_class = FamilyRecordResource
    list_display = (
        "family_member_id",
        "created_at",
        "updated_at",
        "first_name",
        "middle_name",
        "last_name",
        "age",
        "birth_place",
        "citizenship",
        "civil_status",
        "date_of_birth",
        "monthly_income",
        "remarks",
        "gender",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "date_of_birth",
        "gender",
        "citizenship",
        "civil_status",
    )
    search_fields = ("family_member_id", "first_name", "middle_name", "last_name")
    ordering = ("-created_at", "-updated_at")
    list_per_page = 25
    list_max_show_all = 1000
    list_select_related = True


admin.site.register(HouseRecord, HouseRecordAdmin)
admin.site.register(FamilyMember, FamilyRecordAdmin)
