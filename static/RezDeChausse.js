
// Les constantes globales
//--------------------------

const ModeCombo = document.getElementById("mode-Combo");
const HCombo = document.getElementById("h-combo");
const MCombo = document.getElementById("m-combo");
const JourCombo = document.getElementById("jour-Combo");
const apply_config_req = document.getElementById("Apply_config_req");
const plus_config_req = document.getElementById("Plus_config_req");
const minus_config_req = document.getElementById("Minus_config_req");
const DelPointModal = document.getElementById("DelPointModal");
const DelPointNom = document.getElementById("DelPointNom");
const DelPointJour = document.getElementById("DelPointJour");
const DelPointCombo = document.getElementById("DelPointCombo");
const DelPoint_config_req = document.getElementById("DelPoint_config_req");

//Définition des graphes
const Canvas = document.querySelector("#etatGraph");
const ctx = Canvas.getContext("2d");
const PosMouse = document.querySelector("#posMouse");
const ctxPosMouse = PosMouse.getContext("2d");
const CvsOrdonTitle = document.querySelector("#OrdonTitle");
const CtxOrdonTitle = CvsOrdonTitle.getContext("2d");
const CvsAbscisTitle = document.querySelector("#AbscisTitle");
const CtxAbscisTitle = CvsAbscisTitle.getContext("2d");

// Dictionnaire de correspondance valeur → couleur
const couleurs = {
	0: "black",
	1: "red",
	2: "yellow",
	3: "blue"
};

// Dictionnaire de correspondance valeur → nom de l'état
const nom_state = {
	0: "Off",
	1: "Confort",
	2: "Eco",
	3: "Hors gel"
};

//liste des heures
const HeureOptions = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", 
						"11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"];

//liste des minutes (5 par 5)						
const MinuteOptions = ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"];

//liste des jours de la semaine
const JoursSemaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];


//Variables globales 
//--------------------

// Lors de l'affichage d'une modale, nom de l'élément traité (radiateur ou pièce
let ElemNom = "";
// Lors de l'affichage d'une modale, état courant de l'élément
let ElemEtat = 0;
// Lors de l'affichage d'une modale, forçage de l'élément en heures et minutes, partie heures
let forceheure = 0;
// Lors de l'affichage d'une modale, forçage de l'élément en heures et minutes, partie minutes
let forceminute = 0;
// Lors de l'affichage d'une modale, pointeur sur l'élément (radiateur ou piece)
let itempointer = null;
// Lors de l'affichage d'une modale, type élément (radiateur ou piece)
let IsGroupe = false;
// Lors de l'affichage d'une modale, programmation (par jour de la semaine, liste de points de changements ( heure, minute, nouvel état)
let Schedule = [];

// Affichage du graphe de configuration, jour courant
let CurJour = 0;
// Affichage du graphe de configuration, heure sélectionné
let LockHeure= 0;
// Affichage du graphe de configuration, minute sélectionné
let LockMinute = 0;
// Affichage du graphe de configuration, mode sélectionné
let LockMode = 1;
// Affichage du graphe de configuration, échelle en cours
let scale = 1;
// Affichage du graphe de configuration, échelle en cours
let originX = 0;
// Affichage du graphe de configuration, pointeur de souris actif
let isDragging = false;
// Affichage du graphe de configuration, valeur initiale en X du pointeur de souris
let startX;
// Affichage du graphe de configuration, base destruction point
let LockCancelIndexPoint = 0;
//--------------

// fonction
// Modification de la couleur du rectangle en fonction de l'état du radiateur
function ChangeRadiateurColor() {
	console.log("Changing radiateur colors...");
	// Boucle sur les rectangles SVG
	const items = document.querySelectorAll(".radiateur");
	console.log(`Found ${items.length} radiateurs.`);
	items.forEach((item) => {
		console.log(`radiateur ${item.id}: etat: ${item.dataset.state}`);
		const couleur = couleurs[ item.dataset.state] || "gray"; // défaut si valeur inconnue
		item.dataset.nom_state = nom_state[ item.dataset.state] || "Inconnu";
		item.setAttribute("fill", couleur);
	});
};

// Evènement
// Pour chaque élément de la classe "radiateur"
//	Ajouter l'evènement "Click"
//		Récupérer les infos liées à ce radiateur
//		lancer la modale Main
document.querySelectorAll(".radiateur").forEach((el) => {
	el.addEventListener("click", () => {
		ElemNom = el.dataset.nom;
		ElemEtat = el.dataset.nom_state;
		forceheure = el.dataset.forceheure;
		forceminute = el.dataset.forceminute;
		itempointer = el;
		IsGroupe = false;
		let ScheduleString = el.dataset.schedule;
		ScheduleString = ScheduleString.replace(/'/g, '"');   // conversion rapide vers JSON valide
		Schedule = JSON.parse(ScheduleString);
		//for( let i = 0; i < Schedule.length; i++ ){
		//	console.log(`schedule ${i}: heure: ${Schedule[i].heure} mode: ${Schedule[i].mode}`);
		//}
		StartMainModal();
	});
});

// Evènement
// Pour chaque élément de la classe "piece"
//	Ajouter l'evènement "Click"
//		Si la classe ne contient aucun radiateur, signaler par un popup
//		Récupérer les infos liées au premier radiateur de cette classe
//		lancer la modale Main
document.querySelectorAll(".piece").forEach((el) => {
	el.addEventListener("click", () => {
		console.log(`piece ${el.textContent}`);
		const items = Array.from(document.querySelectorAll(".radiateur"));
		if(items.some((item) => {
			console.log(`radiateur ${item.id}: groupe: ${item.dataset.groupe}`);
			if(item.dataset.groupe === el.textContent.trim()){
				ElemEtat = item.dataset.nom_state;
				forceheure = item.dataset.forceheure;
				forceminute = item.dataset.forceminute;
				let ScheduleString = item.dataset.schedule;
				ScheduleString = ScheduleString.replace(/'/g, '"');   // conversion rapide vers JSON valide
				Schedule = JSON.parse(ScheduleString);
				return true; // arrêter la boucle some
			}
		}) === false){
			alert("Cette pièce n'est pas un groupe.");
		}
		else{
			ElemNom = el.textContent;
			itempointer = el;
			IsGroupe = true;
			StartMainModal();
		}
	});
});

// A l'affichage du plan HTML		
// Change la couleur des radiateurs en fonction de leur etat
ChangeRadiateurColor();


// Fenêtre modale de choix d'action
//----------------------------------

// fonction
// démarre la modale pour choisir l'action à faire
function StartMainModal() {
	MainNom.textContent = ElemNom;
	MainState.textContent = ElemEtat;
    MainModal.style.display = "block";
}

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_Main").onclick = () => {
	MainModal.style.display = "none";
};

// Evènement
// Appui sur le bouton "Modifie une fois"
// Détruire la fenêtre modale
// Lance la fenêtre de modification
modify_req.onclick = () => {
	MainModal.style.display = "none";
	StartForceModal();
};

// Evènement
// Appui sur le bouton "Configure"
// Détruire la fenêtre modale
// Lance la fenêtre de configuration
config_req.onclick = () => {
	MainModal.style.display = "none";
	StartConfigureModal();
};


// Fenêtre modale pour forcer un état sur une durée donnée
//--------------------------------------------------------


// fonction
// démarre la modale pour forcer un état sur une durée
function StartForceModal() {
	// Remplir élément sélectionné et son état actuel
	ModifNom.textContent = ElemNom;
	ModifState.textContent = ElemEtat;

	// Remplir la combobox mode
	ModeCombo.innerHTML = "";
	for (let m = 0; m <= 3; m += 1) {
		const optionElement = document.createElement("option");
		optionElement.value = m;
		optionElement.textContent = nom_state[m];
		ModeCombo.appendChild(optionElement);
	}
	// Définir la valeur initiale
	ModeCombo.value = MainState.textContent === "Off" ? 0 :
	   MainState.textContent === "Confort" ? 1 :
	   MainState.textContent === "Eco" ? 2 :
	   MainState.textContent === "Hors gel" ? 3 : 0; 

	// Remplir la combobox heure
	HCombo.innerHTML = "";
	HeureOptions.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = HeureOptions.indexOf(opt);
		optionElement.textContent = opt;
		HCombo.appendChild(optionElement);
	});
	//definir la valeur initiale
	HCombo.value = forceheure;

	// Remplir la combobox minute
	MCombo.innerHTML = "";
	MinuteOptions.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = MinuteOptions.indexOf(opt) * 5;
		optionElement.textContent = opt;
		MCombo.appendChild(optionElement);
	});
	//definir la valeur initiale
	MCombo.value = (forceminute /5) * 5;

	//Afficher la modale
	ModifModal.style.display = "block";
}

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_Modif").onclick = () => {
	ModifModal.style.display = "none";
};

// fonction
// fin forçage radiateur
// Envoie les nouvelles informations au serveur
// Verifie le reour de l'envoi
// Met à jour les infos locales pour le radiateur sélectionné
function EndModifyRadiateur() {
	// Envoie les nouvelles informations au serveur
	fetch(
		`/radiateur/${encodeURIComponent(itempointer.id)}/set-NewRadiateurState`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ 
				state: parseInt(ModeCombo.value),
				forceheure: parseInt(HCombo.value),
				forceminute: parseInt(MCombo.value)
			}),
		}
	)
	
	// Vérifie le retour de l'envoi
	.then((res) => {
		if (!res.ok) throw new Error("Erreur réseau");
		return res.json().catch(() => ({}));
	})
	
	// Met à jour les infos locales pour le radiateur sélectionné
	.then((data) => {
		if (itempointer) {
			itempointer.dataset.state = ModeCombo.value;
			itempointer.dataset.forceheure = HCombo.value;
			itempointer.dataset.forceminute = MCombo.value;  
		}
		
		// Affiche le nouvel état du radiateur
		MainState.textContent = ModeCombo.value;
		console.log(`État mis à jour : ${ModeCombo.value}`);
		ChangeRadiateurColor();
	})
	
	// En cas d'erreur, message
	.catch((err) => {
		console.error(err);
		alert("Échec de la mise à jour de l'état.");
	});          
}

// fonction
// fin forçage pièce
// Envoie les nouvelles informations au serveur
// Verifie le reour de l'envoi
// Met à jour les infos locales pour tous les radiateurs du groupe
function EndModifyPiece() {
	// Envoie les nouvelles informations au serveur
	fetch(
		`/piece/${encodeURIComponent(itempointer.id)}/set-NewGroupeState`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ 
				state: parseInt(ModeCombo.value),
				forceheure: parseInt(HCombo.value),
				forceminute: parseInt(MCombo.value)
			}),
		}
	)
	
	// Vérifie le retour de l'envoi
	.then((res) => {
		if (!res.ok) throw new Error("Erreur réseau");
		return res.json().catch(() => ({}));
	})
	
	// Met à jour les infos locales pour tous les radiateur du groupe
	.then((data) => {
		const items = document.querySelectorAll(".radiateur");
		items.forEach((item) => {
			if(item.dataset.groupe === itempointer.textContent){
				item.dataset.state = ModeCombo.value;
				item.dataset.forceheure = HCombo.value;
				item.dataset.forceminute = MCombo.value;  
			}
		});

		// Affiche les nouveaux états radiateurs dur le plan
		MainState.textContent = ModeCombo.value;
		console.log(`État mis à jour : ${ModeCombo.value}`);
		ChangeRadiateurColor();
	})
	
	// En cas d'erreur, message
	.catch((err) => {
		console.error(err);
		alert("Échec de la mise à jour de l'état.");
	});
}

// Evènement
// Appui sur le bouton "Modifie"
// Ferme la fenêtre modale
// prise en compte des modifications uniquement si une durée est donnée
// Données traitées en fonction du type de composant radiateur ou pièce
Apply_modif_req.onclick = () => {
	if(((HCombo.value != 0) || (MCombo.value != 0)) &&
		(itempointer != null))
	{
		if( IsGroupe == false){
			//Terminer forçage radiateur
			EndModifyRadiateur();
		}
		else{
			// Terminrt forçage pièce
			EndModifyPiece();   
		}

	}
	else{
		// Durée nulle, pas de forçage
		console.log("Pas de forcage.");
	}
	
	// Fermer la fenêtre
	ModifModal.style.display = "none";
};


// Fenêtre modale pour configurer
//--------------------------------

// fonction
// Dessine le graphe mode en fonction du temps pour un jour donné
function LoadGraphModeTime( NumJour) {
	//value -> nom du jour
	let Jour = JoursSemaine[NumJour];
	//trier suivant les heures croissantes
	Schedule[ Jour].sort((a, b) => (((a.heure * 60) + a.minute) - ((b.heure * 60) + b.minute)));
	// properties
	let width = Canvas.width;
	let height = Canvas.height;
	console.log(`canvas, width= ${width}, height= ${height}`);
	// Effacer le canvas
	ctx.clearRect(0, 0, width, height); 
	//appliquer zoom et translation
	ctx.save();
	ctx.setTransform( scale, 0, 0, 1, originX, 0);
	ctxPosMouse.clearRect(0, 0, width, height); 
	// Dessiner l'axe horizontal'
	let heightCanvasAbsc = CvsAbscisTitle.height;
	CtxAbscisTitle.clearRect(0, 0, width, heightCanvasAbsc); 
	CtxAbscisTitle.beginPath();
	CtxAbscisTitle.moveTo(0, heightCanvasAbsc - 50);
	CtxAbscisTitle.lineTo(0 +((24 *12) *scale) +originX, heightCanvasAbsc - 50);
	CtxAbscisTitle.strokeStyle = "black";
	CtxAbscisTitle.stroke();
	//dessiner les creneaux d'heure
	for (let h = 0; h <= 24; h += 1) {
		let x = 0 +((h *12) *scale) +originX;
		CtxAbscisTitle.beginPath();
		CtxAbscisTitle.moveTo(x, heightCanvasAbsc - 52);
		CtxAbscisTitle.lineTo(x, heightCanvasAbsc - 45);
		CtxAbscisTitle.stroke();
		// Ajouter les étiquettes horaires
		CtxAbscisTitle.fillStyle = "black";
		CtxAbscisTitle.font = "10px Arial";
		CtxAbscisTitle.fillText(h.toString().padStart(2, '0'), x - 5, heightCanvasAbsc - 30);
	}
	//ecrire les modes
	let heightCanvasOrdon = CvsOrdonTitle.height;
	for (let m = 0; m <= 3; m += 1) {
		let y = heightCanvasOrdon - 60 - (m * 50);
		CtxOrdonTitle.fillStyle = "black";
		CtxOrdonTitle.font = "10px Arial";
		CtxOrdonTitle.fillText(nom_state[m],2, y + 3);
	}
	// Dessiner les points et les lignes
	ctx.beginPath();
	//init
	let CurrentMode = 1;
	let CurrentHeure = 0;
	let CurrentMinute = 0;
	let NextMode = 1;
	let NextHeure = 24;
	let NextMinute = 0;
	//pour boucler, récupéter la dernière entrée du jour précédent
	if( NumJour == 0){
		//lundi, prendre le dimanche
		if (Schedule[ JoursSemaine[6]].length > 0){
			CurrentMode = Schedule[ JoursSemaine[6]][(Schedule[ JoursSemaine[6]].length) - 1].mode;
		}
	}
	else{
		//autre jour, prendre le jour précédent
		if (Schedule[ JoursSemaine[NumJour - 1]].length > 0){
			CurrentMode = Schedule[ JoursSemaine[NumJour - 1]][(Schedule[ JoursSemaine[NumJour - 1]].length) - 1].mode;
		}
	}
	for (let i = 0; i < Schedule[ Jour].length; i++) {
		NextMode = Schedule[ Jour][ i].mode;
		NextHeure = Schedule[ Jour][ i].heure;
		NextMinute = Schedule[ Jour][ i].minute;
		if( CurrentMode !== NextMode){
			let x1 = 0 + (CurrentHeure * 12) + ((CurrentMinute / 5) * 1);
			let x2 = 0 + (NextHeure * 12) + ((NextMinute / 5) * 1);
			let y1 = height - 5 - (CurrentMode *50);
			let y2 = height - 5 - (NextMode * 50);
			//ligne horizontale
			ctx.moveTo(x1, y1);
			ctx.lineTo(x2, y1);
			//ligne verticale
			ctx.moveTo(x2, y1);
			ctx.lineTo(x2, y2);
			CurrentMode = NextMode;
			CurrentHeure = NextHeure;
			CurrentMinute = NextMinute;
		}
	}
	// ligne finale jusqu'à 24h
	if( CurrentHeure < 24){
		let x1 = 0 + (CurrentHeure * 12) + ((CurrentMinute / 5) * 1);
		let x2 = 0 + (24 * 12);
		let y1 = height - 5 - (CurrentMode *50);
		ctx.moveTo(x1, y1);
		ctx.lineTo(x2, y1);
	}
	ctx.stroke(); 

	//init
	CurrentMode = 1;
	CurrentHeure = 0;
	CurrentMinute = 0;
	NextMode = 1;
	NextHeure = 24;
	NextMinute = 0;
	const ZoneLabels = document.getElementById("zone-labels");
	ZoneLabels.innerHTML = "";

	//pour boucler, récupéter la dernière entrée du jour précédent
	if( NumJour == 0){
		//lundi, prendre le dimanche
		if (Schedule[ JoursSemaine[6]].length > 0){
			CurrentMode = Schedule[ JoursSemaine[6]][(Schedule[ JoursSemaine[6]].length) - 1].mode;
		}
	}
	else{
		//autre jour, prendre le jour précédent
		if (Schedule[ JoursSemaine[NumJour - 1]].length > 0){
			CurrentMode = Schedule[ JoursSemaine[NumJour - 1]][(Schedule[ JoursSemaine[NumJour - 1]].length) - 1].mode;
		}
	}
	for (let i = 0; i < Schedule[ Jour].length; i++) {
		NextMode = Schedule[ Jour][ i].mode;
		NextHeure = Schedule[ Jour][ i].heure;
		NextMinute = Schedule[ Jour][ i].minute;
		const label = document.createElement("label");
		label.textContent = 
		NextHeure.toString().padStart(2, '0') +"H" +NextMinute.toString().padStart(2, '0') +", " +
		nom_state[NextMode];
		if( CurrentMode === NextMode){
			label.textContent = label.textContent +"; Inactif"
		}
		ZoneLabels.appendChild(label);
		ZoneLabels.appendChild(document.createElement("br"));

		CurrentMode = NextMode;
		CurrentHeure = NextHeure;
		CurrentMinute = NextMinute;
	}
}

// fonction
// démarre la modale pour configurer la programmation
function StartConfigureModal() {
	//nom du radiateur ou de la pièce
	ConfigNom.textContent = ElemNom;

	// Remplir la combobox jours
	JourCombo.innerHTML = "";
	JoursSemaine.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = JoursSemaine.indexOf(opt);
		optionElement.textContent = opt;
		JourCombo.appendChild(optionElement);
	});
	
	// Définir la valeur initiale
	JourCombo.value = 0; // Par défaut Lundi
	CurJour = 0;
	scale = 1;
	originX = 0;
	isDragging = false; 
	
	//Charger le graphe
	LoadGraphModeTime( JourCombo.value );

	// Ovrir la fenêtre
	ConfigModal.style.display = "block";
}

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_Config").onclick = () => {
	ConfigModal.style.display = "none";
};

// Evènement
// ----- zoom à la molette -----
Canvas.addEventListener("wheel", (e) => {
	e.preventDefault();

	const zoomIntensity = 0.1;
	const mouseX = e.offsetX;

	// zoom sur le point du curseur
	const wheel = e.deltaY < 0 ? 1 : -1;
	const zoom = Math.exp(wheel * zoomIntensity);
	
	//Calcul du rapport d'agrandissement
	scale *= zoom;
	if( scale < 1)
	{
		scale = 1;
	}
	
	//recharger le graphe
	LoadGraphModeTime( CurJour );
});

// Evènement
// ----- pan (clic + glisser) début -----
Canvas.addEventListener("mousedown", (e) => {
	// En mouvement
	isDragging = true;
	// Mémorisation du point de départ
	startX = e.offsetX - originX;
});

// Evènement
// ----- pan (clic + glisser) fin -----
Canvas.addEventListener("mouseup", () => {
	// Fin du mouvement
	isDragging = false;
});

// Evènement
// ----- pan (clic + glisser) en cours -----
Canvas.addEventListener("mousemove", function(event) {
	const rect = Canvas.getBoundingClientRect();
	const x = (event.clientX - rect.left -originX) /scale;
	const y = event.clientY - rect.top;

	// si mouvement en cours
	if (isDragging) {
		if((event.offsetX - startX) > 0)
		{
			//bloquer l'origine a 0 si negatif
			originX = 0;
		}
		else
		{
			// Calcul de la nouvelle origine
			originX = event.offsetX - startX;
		}
	}

	// Effacer le canvas de position de la souris
	ctxPosMouse.clearRect(0, 0, PosMouse.width, PosMouse.height);
	ctxPosMouse.fillStyle = "black";
	ctxPosMouse.font = "16px Arial";
	if((Math.floor(x) >= 0) && 
		(Math.floor(x) <= 616) &&
		(Math.floor(y) <= (Canvas.height - 0)) && 
		(Math.floor(y) >= (Canvas.height - 175))
		)
	{
		//convertir l'abcisse en heure et minute
		let curheure = Math.floor((x - 0) / 12);
		let curminute = Math.floor(((x -0) % 12) / 1) * 5;
		//convertir l'ordonnée en mode
		let curmode = 0;
		if((Math.floor(y) <= (Canvas.height - 25) && 
			(Math.floor(y) > (Canvas.height - 75)))){
			curmode = 1;
		}
		else if((Math.floor(y) <= (Canvas.height - 75) && 
			(Math.floor(y) > (Canvas.height - 125)))){
			curmode = 2;
		}
		else if(Math.floor(y) <= (Canvas.height - 125)){
			curmode = 3;
		}
		ctxPosMouse.fillText(`heure: ${curheure.toString().padStart(2, '0')} : ${curminute.toString().padStart(2, '0')} - mode: ${nom_state[curmode]}`, 10, 20);
		ctxPosMouse.fillText(`posx: ${event.offsetX.toString()} ,x: ${x.toString()} ,y: ${y.toString()}`, 10, 40);
		ctxPosMouse.fillText(`origine: ${originX.toString()} ,scale: ${scale.toString()}`, 10, 60);
	}
	
	//reconstruire le graphe si mouvement en cours
	if (isDragging) {
		LoadGraphModeTime( CurJour );
	}
});

// Evènement
// ----- double click -----
Canvas.addEventListener("dblclick", function(event) {
	const rect = Canvas.getBoundingClientRect();
	const x = (event.clientX - rect.left -originX) /scale;
	const y = event.clientY - rect.top;

	// Check if within valid area
	if((Math.floor(x) >= 0) && 
		(Math.floor(x) <= 616) &&
		(Math.floor(y) <= (Canvas.height - 0)) && 
		(Math.floor(y) >= (Canvas.height - 175))
		)
	{
		//convertir l'abcisse en heure et minute
		LockHeure = Math.floor((x - 0) / 12);
		LockMinute = Math.floor(((x - 0) % 12) / 1) * 5;
		//convertir l'ordonnée en mode
		LockMode = 0;
		if((Math.floor(y) <= (Canvas.height - 25) && 
			(Math.floor(y) > (Canvas.height - 75)))){
			LockMode = 1;
		}
		else if((Math.floor(y) <= (Canvas.height - 75) && 
			(Math.floor(y) > (Canvas.height - 125)))){
			LockMode = 2;
		}
		else if(Math.floor(y) <= (Canvas.height - 125)){
			LockMode = 3;
		}
		console.log(`Lock heure: ${LockHeure.toString().padStart(2, '0')} : ${LockMinute.toString().padStart(2, '0')} - mode: ${nom_state[LockMode]}`);

		//lancer la modale Add / del point
		StartAddDelPointModal();
	}
});

// Evènement
// ----- nouvelle valeur dans la combo jour -----
document.getElementById("jour-Combo").addEventListener("change", function(){
	//récupérer le nouveau jour
	console.log(`Jour selectionné: ${JoursSemaine[this.value]}`);
	CurJour = this.value;
	// Valeur par défaut agrandissement, origine, mouvement en cours
	scale = 1;
	originX = 0;
	isDragging = false; 
	
	//Graphe du jour sélectionné
	LoadGraphModeTime( CurJour );
});

// fonction
// Envoie les nouvelles informations au serveur
// Contrôle si l'envoi au serveur s'est bien passé
// met à jour la configuration locale
// pop up en cas d'erreur
function EndConfigRadiateur() {
	// Envoie les nouvelles informations au serveur
	fetch(
		`/radiateur/${encodeURIComponent(itempointer.id)}/set-NewRadiateurConfig`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ 
				DayConfigs: Schedule
			}),
		}
	)
	
	// Verifie que l'envoi est sans erreur
	.then((res) => {
		if (!res.ok) throw new Error("Erreur réseau");
		return res.json().catch(() => ({}));
	})
	
	// Met à jour les infos locales
	.then((data) => {
		itempointer.dataset.schedule = JSON.stringify(Schedule);
		console.log(`Configuration par jour mise à jour`);
	})
	
	// En cas d'envoi avec erreur
	.catch((err) => {
		console.error(err);
		alert("Échec de la mise à jour de la configuration par jour");
	});          
};

// fonction
// Envoie les nouvelles informations au serveur
// Contrôle si l'envoi au serveur s'est bien passé
// met à jour la configuration locale
// pop up en cas d'erreur
function EndConfigPiece() {
	// Envoie les nouvelles informations au serveur
	fetch(
		`/piece/${encodeURIComponent(itempointer.id)}/set-NewGroupeConfig`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ 
				DayConfigs: Schedule
			}),
		}
	)
	
	// Verifie que l'envoi est sans erreur
	.then((res) => {
		if (!res.ok) throw new Error("Erreur réseau");
		return res.json().catch(() => ({}));
	})
	
	// Met à jour les infos locales
	.then((data) => {
		const items = document.querySelectorAll(".radiateur");
		items.forEach((item) => {
			if(item.dataset.groupe === itempointer.textContent){
				item.dataset.schedule = JSON.stringify(Schedule);
			}
		});
		console.log(`Configuration par jour mise à jour`);
	})
	
	// En cas d'envoi avec erreur
	.catch((err) => {
		console.error(err);
		alert("Échec de la mise à jour de la configuration par jour");
	});          
};

// Evènement
// Appui sur le bouton "Applique"
// Ferme la fenêtre avec prise en compte des informations
// traite en fonction du type d'élément (raditeur ou piece)
apply_config_req.onclick = () => {
	if( IsGroupe == false){
		//Terminer forçage radiateur
		EndConfigRadiateur();
	}
	else{
		// Terminrt forçage pièce
		EndConfigPiece();   
	}
	
	// Fermer la fenêtre
	ConfigModal.style.display = "none";
};

// Evènement
// Appui sur le bouton "Duplique"
// Duplique la programmation du jour courant sur tous les autres jours
Duplicate_config_req.onclick = () => {
	let Jour = JoursSemaine[CurJour];
	for( const key in Schedule) {
		if( key !== Jour) {
			Schedule[ key] = Schedule[ Jour];
		}
	}
	LoadGraphModeTime( CurJour );
};

// Evènement
// Appui sur le bouton plus
// Démarre la modale pour ajouter un point
plus_config_req.onclick = () => {
	StartAddPointModal();
};

// Evènement
// Appui sur le bouton moins
// Démarre la modale pour effacer un point
minus_config_req.onclick = () => {
	StartDelPointModal();
};


//Fenêtre modale pour ajouter ou détruire un Point
//--------------------------------------------------

//fonction
//Démarre la fenêtre modale pour ajouter ou détruire un point		
function StartAddDelPointModal() {
	let Jour = JoursSemaine[CurJour];
	AddDelPointNom.textContent = ConfigNom.textContent;
	AddDelPointJour.textContent = `Jour: ${Jour}`;
	// Remplir la combobox mode
	AddDelModeCombo.innerHTML = "";
	for (let i = 0; i <= 3; i++) {
		const Item= document.createElement("option");
		Item.value = i;
		Item.textContent = nom_state[i];
		AddDelModeCombo.appendChild(Item);
	}
	AddDelModeCombo.value = LockMode;

	// Remplir les combobox temps (heure et minutes)
	AddDelHeureCombo.innerHTML = "";
	if( LockHeure >= 1) {
		LockHeure = LockHeure -1;
	}
	if( LockHeure == 22) {
		LockHeure = LockHeure -1;
	}
	for( let I = 0; I < 3; I++) {
		const optionElement = document.createElement("option");
		optionElement.value = I;
		optionElement.textContent = (LockHeure +I).toString().padStart(2, '0');
		AddDelHeureCombo.appendChild(optionElement);
	}
	AddDelHeureCombo.value = 1;

	// Remplir les combobox minutes
	AddDelMinuteCombo.innerHTML = "";
	MinuteOptions.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = MinuteOptions.indexOf(opt) * 5;
		optionElement.textContent = opt;
		AddDelMinuteCombo.appendChild(optionElement);
	});
	AddDelMinuteCombo.value = LockMinute;

	AddDelPointCombo.innerHTML = "";
	let nbPoints = 0;
	LockCancelIndexPoint = -1;
	for (let i = 0; i < Schedule[ Jour].length; i++) {
		if((Schedule[Jour][i].heure >= LockHeure) &&
		  (Schedule[Jour][i].heure <= LockHeure +2)) {
			if( LockCancelIndexPoint == -1) {
				LockCancelIndexPoint = i;
			}
			const Item= document.createElement("option");
			Item.value = nbPoints;
			nbPoints ++;
			Item.textContent = 
			`${Schedule[Jour][i].heure.toString().padStart(2, '0')}H${Schedule[ Jour][i].minute.toString().padStart(2, '0')} - ${nom_state[Schedule[ Jour][i].mode]}`;
			AddDelPointCombo.appendChild(Item);
		}
	}
	AddDelPointCombo.value = 0;

	//afficher la fenêtre
	AddDelPointModal.style.display = "block";
};

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_AddDelPoint").onclick = () => {
	AddDelPointModal.style.display = "none";
};

// Evènement
// Appui sur le bouton "Efface"
// prend en compte la demande et détruit la fenêtre modale
// reconstruit le graphe du jour
DelPoint_AddDelconfig_req.onclick = () => {
	if( LockCancelIndexPoint != -1) {
		//value -> nom du jour
		let Jour = JoursSemaine[CurJour];
		const indexToDelete = parseInt(AddDelPointCombo.value) +LockCancelIndexPoint;
		if( isNaN(indexToDelete) || indexToDelete < 0 || indexToDelete >= Schedule[ Jour].length){
			alert("Index invalide.");
			return;
		}
		Schedule[ Jour].splice(indexToDelete, 1);
		alert(`Point ${indexToDelete} supprimé.`);
		AddDelPointModal.style.display = "none";
		LoadGraphModeTime( CurJour );
	}
};


// Evènement
// Appui sur le bouton "Ajout"
// prend en compte la demande et détruit la fenêtre modale
// reconstruit le graphe du jour
AddPoint_AddDelconfig_req.onclick = () => {
	//value -> nom du jour
	let Jour = JoursSemaine[CurJour];
	const newHeure = parseInt(AddDelHeureCombo.value) +LockHeure;
	const newMinute = parseInt(AddDelMinuteCombo.value);
	const newMode = parseInt(AddDelModeCombo.value);
	//vérifier si le point existe déjà
	const exists = Schedule[ Jour].some(point => point.heure === newHeure && point.minute === newMinute);
	if( exists ){
		alert("Un point existe déjà à cette heure.");
		return;
	}
	//ajouter le point
	Schedule[ Jour].push({ heure: newHeure, minute: newMinute, mode: newMode });
	alert(`Point ajouté: ${newHeure.toString().padStart(2, '0')}H${newMinute.toString().padStart(2, '0')} - ${nom_state[newMode]}`);
	AddDelPointModal.style.display = "none";
	LoadGraphModeTime( CurJour );
};


//Fenêtre modale pour ajouter un Point
//--------------------------------------

//fonction
//Démarre la fenêtre modale pour ajouter un point		
function StartAddPointModal() {
	//value -> nom du jour
	let Jour = JoursSemaine[CurJour];
	AddPointNom.textContent = ConfigNom.textContent;
	AddPointJour.textContent = `Jour: ${Jour}`;
	// Remplir les combobox modes
	AddModeCombo.innerHTML = "";
	for (let i = 0; i <= 3; i++) {
		const Item= document.createElement("option");
		Item.value = i;
		Item.textContent = nom_state[i];
		AddModeCombo.appendChild(Item);
	}
	AddModeCombo.value = 1; // Par défaut Confort

	// Remplir les combobox heures
	AddHeureCombo.innerHTML = "";
	HeureOptions.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = HeureOptions.indexOf(opt);
		optionElement.textContent = opt;
		AddHeureCombo.appendChild(optionElement);
	});
	AddHeureCombo.value = 0; // Par défaut 00

	// Remplir les combobox minutes
	AddMinuteCombo.innerHTML = "";
	MinuteOptions.forEach(opt => {
		const optionElement = document.createElement("option");
		optionElement.value = MinuteOptions.indexOf(opt) * 5;
		optionElement.textContent = opt;
		AddMinuteCombo.appendChild(optionElement);
	});
	AddMinuteCombo.value = 0; // Par défaut 00

	AddPointModal.style.display = "block";
};

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_AddPoint").onclick = () => {
	AddPointModal.style.display = "none";
};

// Evènement
// Appui sur le bouton "Ajout"
// prend en compte la demande et détruit la fenêtre modale
// reconstruit le graphe du jour
AddPoint_config_req.onclick = () => {
	//value -> nom du jour
	let Jour = JoursSemaine[CurJour];
	const newHeure = parseInt(AddHeureCombo.value);
	const newMinute = parseInt(AddMinuteCombo.value);
	const newMode = parseInt(AddModeCombo.value);
	//vérifier si le point existe déjà
	const exists = Schedule[ Jour].some(point => point.heure === newHeure && point.minute === newMinute);
	if( exists ){
		alert("Un point existe déjà à cette heure.");
		return;
	}
	//ajouter le point
	Schedule[ Jour].push({ heure: newHeure, minute: newMinute, mode: newMode });
	alert(`Point ajouté: ${newHeure.toString().padStart(2, '0')}H${newMinute.toString().padStart(2, '0')} - ${nom_state[newMode]}`);
	AddPointModal.style.display = "none";
	LoadGraphModeTime( CurJour );
};


// Fenêtre modale pour détruire un Point
//---------------------------------------

//fonction
//Démarre la fenêtre modale pour détruire un point		
function StartDelPointModal() {
	//value -> nom du jour
	let Jour = JoursSemaine[CurJour];
	DelPointNom.textContent = ConfigNom.textContent;
	DelPointJour.textContent = `Jour: ${Jour}`;
	// Remplir la combobox points existants
	DelPointCombo.innerHTML = "";
	for (let i = 0; i < Schedule[ Jour].length; i++) {
		const Item= document.createElement("option");
		Item.value = i;
		Item.textContent = 
		  `${Schedule[Jour][i].heure.toString().padStart(2, '0')}H${Schedule[ Jour][i].minute.toString().padStart(2, '0')} - ${nom_state[Schedule[ Jour][i].mode]}`;
		DelPointCombo.appendChild(Item);
	}
	DelPointCombo.value = 0; // Par défaut le premier
	DelPointModal.style.display = "block";
};

// Evènement
// Appui sur le bouton "fermer la fenêtre"
// Détruire la fenêtre modale sans rien enregistrer
document.getElementById("closeModal_DelPoint").onclick = () => {
	DelPointModal.style.display = "none";
};

// Evènement
// Appui sur le bouton "Efface"
// prend en compte la demande et détruit la fenêtre modale
// reconstruit le graphe du jour
DelPoint_config_req.onclick = () => {
	//value -> nom du jour
	let Jour = JoursSemaine[CurJour];
	const indexToDelete = parseInt(DelPointCombo.value);
	if( isNaN(indexToDelete) || indexToDelete < 0 || indexToDelete >= Schedule[ Jour].length){
		alert("Index invalide.");
		return;
	}
	Schedule[ Jour].splice(indexToDelete, 1);
	alert(`Point ${indexToDelete} supprimé.`);
	DelPointModal.style.display = "none";
	LoadGraphModeTime( CurJour );
};

// voir si nécessaire
//        window.onclick = (event) => {
//          if (event.target === MainModal) MainModal.style.display = "none";
//          if (event.target === ModifModal) ModifModal.style.display = "none";
//          if (event.target === ConfigModal) ConfigModal.style.display = "none";
//        };
