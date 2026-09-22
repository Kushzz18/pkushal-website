(function(){
  var nt=document.getElementById('navToggle'), nl=document.getElementById('navLinks');
  if(nt&&nl){
    nt.addEventListener('click',function(){var o=nl.classList.toggle('open');nt.setAttribute('aria-expanded',o?'true':'false');});
    nl.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){nl.classList.remove('open');nt.setAttribute('aria-expanded','false');});});
  }
})();
