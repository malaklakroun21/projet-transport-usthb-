from django.shortcuts import render, get_object_or_404, redirect
from .models import Expedition
from .forms import ExpeditionForm


# Create your views here.

def expedition_list(request):
    expeditions = Expedition.objects.all().order_by("-id")
    return render(request, "logistics/expedition_list.html", {"expeditions": expeditions})


def expedition_detail(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)
    return render(request, "logistics/expedition_detail.html", {"expedition": expedition})


def create_expedition(request):
    if request.method == "POST":
        form = ExpeditionForm(request.POST)
        if form.is_valid():
            expedition = form.save()
            # TODO: adjust redirect name to your urls.py name if different
            return redirect("expedition_detail", pk=expedition.pk)
    else:
        form = ExpeditionForm()

    return render(request, "logistics/create_expedition.html", {"form": form})


def update_expedition(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)

    if request.method == "POST":
        form = ExpeditionForm(request.POST, instance=expedition)
        if form.is_valid():
            expedition = form.save()
            # TODO: adjust redirect name to your urls.py name if different
            return redirect("expedition_detail", pk=expedition.pk)
    else:
        form = ExpeditionForm(instance=expedition)

    return render(
        request,
        "logistics/update_expedition.html",
        {"form": form, "expedition": expedition},
    )


def delete_expedition(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)

    # Verification: only delete on POST (prevents accidental deletes via URL)
    if request.method == "POST":
        expedition.delete()
        # TODO: adjust redirect name to your urls.py name if different
        return redirect("expedition_list")

    return render(request, "logistics/delete_expedition.html", {"expedition": expedition})
