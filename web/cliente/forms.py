from django import forms


class UploadArquivoETLForm(forms.Form):
    arquivo = forms.FileField(
        label="Arquivo CSV",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".csv",
            }
        ),
    )

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        if not arquivo.name.lower().endswith(".csv"):
            raise forms.ValidationError("Envie um arquivo com extensão .csv.")
        return arquivo