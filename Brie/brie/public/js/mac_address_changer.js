function mac_address_correcter(event){
    var valeur = document.getElementById("mac_adress_input").value;
    console.log(document.getElementById("mac_adress_input").value);
    var regex = /&/g;
    valeur = valeur.replace(regex, "1");    
    var regex = /é/g;
    valeur = valeur.replace(regex, "2");    
    var regex = /"/g;
    valeur = valeur.replace(regex, "3");    
    var regex = /'/g;
    valeur = valeur.replace(regex, "4");    
    var regex = /\(/g;
    valeur = valeur.replace(regex, "5");    
    var regex = /-/g;
    valeur = valeur.replace(regex, "6");    
    var regex = /è/g;
    valeur = valeur.replace(regex, "7");    
    var regex = /_/g;
    valeur = valeur.replace(regex, "8");    
    var regex = /ç/g;
    valeur = valeur.replace(regex, "9");    
    var regex = /à/g;
    valeur = valeur.replace(regex, "0");
    if(document.getElementById("mac_adress_input").value != valeur){
        document.getElementById("mac_adress_input").value = valeur;
    }
    var regex = /[^A-Fa-f0-9:]/gi;
    if(valeur.search(regex) != -1)
        alert("ERREUR");
}
