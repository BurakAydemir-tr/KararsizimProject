from django import forms
from django.core.exceptions import ValidationError
from .services import normalize_options
from .models import Report


class PollForm(forms.Form):
    duration = forms.ChoiceField(label="Oylama süresi", required=False,
        choices=[("", "Süresiz"), ("1", "1 saat"), ("24", "24 saat"), ("168", "7 gün")])
    question = forms.CharField(label="Sorun", min_length=10, max_length=200, help_text="10–200 karakter. Kararsız kaldığın konuyu açıkça sor.", widget=forms.Textarea(attrs={"rows": 2}))
    description = forms.CharField(label="Açıklama (isteğe bağlı)", max_length=500, required=False, help_text="En fazla 500 karakter. Karar vermeye yardımcı olacak ayrıntıları ekle.", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for number in range(1, 6):
            self.fields[f"option_{number}"] = forms.CharField(label=f"Seçenek {number}", max_length=100, required=False, help_text="En fazla 100 karakter.")

    def clean(self):
        data = super().clean()
        if any(key.startswith("option_") and key not in self.fields for key in self.data):
            raise ValidationError("En fazla 5 seçenek ekleyebilirsin.")
        data["options"] = normalize_options([data.get(f"option_{i}", "") for i in range(1, 6)])
        return data


class VoteForm(forms.Form):
    choice = forms.IntegerField(min_value=1, error_messages={"required": "Önce bir seçenek seçmelisin.", "invalid": "Geçerli bir seçenek seçmelisin."})


class ReportForm(forms.Form):
    reason = forms.ChoiceField(label="Bildirim nedeni", choices=Report.REASONS)
    description = forms.CharField(label="Açıklama", max_length=500, required=False,
                                  help_text="Parola veya kişisel bilgi paylaşma.", widget=forms.Textarea(attrs={"rows": 3}))
