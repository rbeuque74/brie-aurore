function mac_address_correcter(event){
    if($("#disablevalid:checked").length == 1){ return; }
    //si on tape sur backspace ou delete
    if(event.keyCode == 8 || event.keyCode == 46) { return; }
    var valeur = $(this).val();
    var os = $("#osRegister").val();
    console.log(valeur);
    var regex = Array();
    regex['win'] = Array(/&/g, /é/g, /"/g, /'/g, /\(/g, /-/g, /è/g, /_/g, /ç/g, /à/g);
    regex['mac'] = Array(/&/g, /é/g, /"/g, /'/g, /\(/g, /§/g, /è/g, /\!/g, /ç/g, /à/g);
    valeur = valeur.replace(regex[os][0], "1");    
    valeur = valeur.replace(regex[os][1], "2");    
    valeur = valeur.replace(regex[os][2], "3");    
    valeur = valeur.replace(regex[os][3], "4");    
    valeur = valeur.replace(regex[os][4], "5");    
    valeur = valeur.replace(regex[os][5], "6");    
    valeur = valeur.replace(regex[os][6], "7");    
    valeur = valeur.replace(regex[os][7], "8");    
    valeur = valeur.replace(regex[os][8], "9");    
    valeur = valeur.replace(regex[os][9], "0");
    if(valeur.length == 2 || valeur.length == 5 || valeur.length == 8 || valeur.length == 11 || valeur.length == 14){
        valeur = valeur + ":";
        $(this).val(valeur);
    }
    var regex = /::/g;
    valeur = valeur.replace(regex, ":");
    if($(this).val() != valeur){
        $(this).val(valeur);
    }
    var regex = /[^A-Fa-f0-9:]/gi;
    if(valeur.search(regex) != -1 || valeur.length > 17){
        $(this).parent().find(".macInvalid").css("display", "inline");
        $(this).css("color", "red");
    } else {
        $(this).parent().find(".macInvalid").css("display", "none");
        $(this).css("color", "");
    }
}
compteur = 1;
function addMacField(){
    compteur++;
    if(compteur > 4){
        alert("Oui enfin bon on va pas en ajouter 50 non plus...");
        return;
    }
    $("#machine_add").append($("<div></div>"));
    $("#machine_add div").last().append($("<input></input>").attr("type","text").attr("id", "name_machine_input_"+compteur).attr("placeholder","nom de la machine").addClass("item_name"));
    $("#machine_add div").last().append($("<input></input>").attr("type","text").attr("placeholder","adresse mac").attr("id", "mac_adress_input_"+compteur).addClass("macValidator"));
    $("#machine_add div").last().append($("<span>adresse mac invalide</span>").addClass("macInvalid"));
    if(compteur == 2){
        $("#machine_add #name_machine_input_"+compteur).attr("name","second_machine_name");
        $("#machine_add #mac_adress_input_"+compteur).attr("name","second_machine_mac");
    } else if(compteur == 3){
        $("#machine_add #name_machine_input_"+compteur).attr("name","third_machine_name");
        $("#machine_add #mac_adress_input_"+compteur).attr("name","third_machine_mac");
    } else if(compteur == 4){
        $("#machine_add #name_machine_input_"+compteur).attr("name","fourth_machine_name");
        $("#machine_add #mac_adress_input_"+compteur).attr("name","fourth_machine_mac");
    }
}

$(document).ready(function(){
    $(document).on("keyup", ".macValidator", mac_address_correcter);
});
