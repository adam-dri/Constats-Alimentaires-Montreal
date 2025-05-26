/**
 * Empêche l'envoi du formulaire si aucun critère n'est renseigné.
 * @returns {boolean}
 */
function validerFormulaire() {
  const etablissement = document.querySelector('input[name="etablissement"]').value.trim();
  const proprietaire = document.querySelector('input[name="proprietaire"]').value.trim();
  const rue = document.querySelector('input[name="rue"]').value.trim();

  if (!etablissement && !proprietaire && !rue) {
      alert('Veuillez saisir au moins un critère de recherche.');
      return false;
  }
  return true;
}


/**
 * Charge la liste des établissements dans le menu déroulant.
 */
function chargerListeEtablissements() {
  fetch("/etablissements")
    .then(function(reponse) {
      return reponse.json();
    })
    .then(function(donnees) {
      var selection = document.getElementById("select-etablissement");
      donnees.forEach(function(nom) {
        var option = document.createElement("option");
        option.value = nom;
        option.textContent = nom;
        selection.appendChild(option);
      });
    })
    .catch(function(erreur) {
      console.error("Erreur de chargement des établissements :", erreur);
    });
}


/**
 * Effectue la recherche AJAX entre deux dates et affiche les résultats (A5).
 */
function rechercheDates() {
  const dateDebut = document.getElementById('date-debut').value;
  const dateFin = document.getElementById('date-fin').value;

  if (!dateDebut || !dateFin) {
      alert('Veuillez sélectionner une date de début et une date de fin.');
      return;
  }

  const aujourdHui = new Date().toISOString().split('T')[0];
  if (dateDebut > aujourdHui || dateFin > aujourdHui) {
      alert('Les dates ne peuvent pas dépasser la date du jour.');
      return;
  }

  fetch(`/contrevenants?du=${dateDebut}&au=${dateFin}`)
      .then(response => {
          if (!response.ok) throw new Error(response.statusText);
          return response.json();
      })
      .then(data => {
          const stats = {};
          data.forEach(item => {
              const nom = item.etablissement;
              stats[nom] = (stats[nom] || 0) + 1;
          });

          const container = document.getElementById('resultats-dates');
          let tableau = `
              <table class="tableau">
                  <thead>
                      <tr><th>Établissement</th><th>Nombre de contraventions</th></tr>
                  </thead>
                  <tbody>
          `;
          for (const nom in stats) {
              tableau += `
                      <tr>
                          <td>${nom}</td>
                          <td>${stats[nom]}</td>
                      </tr>
              `;
          }
          tableau += '</tbody></table>';
          container.innerHTML = tableau;
      })
      .catch(error => {
          console.error('Erreur durant la recherche par période :', error);
          alert('Une erreur est survenue lors de la recherche.');
      });
}


/**
 * Recherche AJAX des infractions pour l'établissement sélectionné (A6).
 */
function rechercherParEtablissement() {
  const select = document.getElementById('select-etablissement');
  const nom = select.value;

  if (!nom) {
      alert('Veuillez sélectionner un établissement.');
      return;
  }

  fetch(`/infractions?etablissement=${encodeURIComponent(nom)}`)
      .then(response => {
          if (!response.ok) throw new Error(response.statusText);
          return response.json();
      })
      .then(data => {
          const container = document.getElementById('resultats-etablissement');
          if (data.length === 0) {
              container.innerHTML = '<p>Aucune infraction pour cet établissement.</p>';
              return;
          }

          let tableau = `
              <table class="tableau">
                  <thead>
                      <tr>
                          <th>Date</th><th>Description</th><th>Adresse</th>
                          <th>Montant</th><th>Catégorie</th>
                      </tr>
                  </thead>
                  <tbody>
          `;
          data.forEach(contrav => {
              tableau += `
                      <tr>
                          <td>${contrav.date}</td>
                          <td>${contrav.description}</td>
                          <td>${contrav.adresse}</td>
                          <td>${contrav.montant} $</td>
                          <td>${contrav.categorie}</td>
                      </tr>
              `;
          });
          tableau += '</tbody></table>';
          container.innerHTML = tableau;
      })
      .catch(error => {
          console.error('Erreur lors de la récupération des infractions :', error);
          alert('Impossible de récupérer les infractions.');
      });
}


// Initialisation au chargement de la page
window.addEventListener("load", function() {
  var dateDuJour = new Date().toISOString().split("T")[0];
  var debut = document.getElementById("date-debut");
  var fin = document.getElementById("date-fin");
  if (debut) {
    debut.max = dateDuJour;
    debut.addEventListener("change", function() {
      fin.min = this.value;
      if (fin.value < this.value) fin.value = this.value;
    });
  }
  if (fin) fin.max = dateDuJour;

  chargerListeEtablissements();
});



// E2
let selection = [];

function rechercherEtablissements(evenement) {
    evenement.preventDefault();

    let champ = document.getElementById("champ-recherche");
    let entree = champ.value;

    fetch("/rechercher-etablissements?entree=" + encodeURIComponent(entree))
        .then(function(reponse) {
            return reponse.json();
        })
        .then(function(donnees) {
            let liste = document.getElementById("liste-resultats");
            liste.innerHTML = "";

            for (let i = 0; i < donnees.length; i++) {
                let element = donnees[i];
                let item = document.createElement("li");
                item.textContent = element.id + " - " + element.nom;
                item.onclick = function() {
                    if (!selection.includes(String(element.id))) {
                        selection.push(String(element.id));
                        afficherSelection();
                    }
                };
                liste.appendChild(item);
            }
        });
}

function afficherSelection() {
    let liste = document.getElementById("liste-selection");
    liste.innerHTML = "";

    for (let i = 0; i < selection.length; i++) {
        let item = document.createElement("li");
        item.textContent = selection[i];
        liste.appendChild(item);
    }

    document.getElementById("champs-selection").value = selection.join(",");
}