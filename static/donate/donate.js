
function myfunction(id){


var  btnCopy = document.getElementById(id);
var toCopy  = document.getElementById(id.concat("text"));
    toCopy.select();
  
    if ( document.execCommand( 'copy' ) ) {

        btnCopy.classList.add( 'copied' );

        var temp = setInterval( function(){
          btnCopy.classList.remove( 'copied' );
          clearInterval(temp);
        }, 600 );
      
    } else {
      console.info( 'document.execCommand went wrong…' )
    }
  
  }

  
  
