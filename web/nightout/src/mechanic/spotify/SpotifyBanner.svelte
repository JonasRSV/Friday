<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row } from 'sveltestrap';

</script>


<style>

  .vertical-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
  }

  .banner {
    border-radius: 10px;
    width: 100%;
    height: 120px;
    /*background-size: cover;*/

    background-color: #0de126;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 1000'%3E%3Cg %3E%3Ccircle fill='%230de126' cx='50' cy='0' r='50'/%3E%3Cg fill='%2300d529' %3E%3Ccircle cx='0' cy='50' r='50'/%3E%3Ccircle cx='100' cy='50' r='50'/%3E%3C/g%3E%3Ccircle fill='%2300c92b' cx='50' cy='100' r='50'/%3E%3Cg fill='%2300bd2d' %3E%3Ccircle cx='0' cy='150' r='50'/%3E%3Ccircle cx='100' cy='150' r='50'/%3E%3C/g%3E%3Ccircle fill='%2300b12e' cx='50' cy='200' r='50'/%3E%3Cg fill='%2300a62e' %3E%3Ccircle cx='0' cy='250' r='50'/%3E%3Ccircle cx='100' cy='250' r='50'/%3E%3C/g%3E%3Ccircle fill='%23009a2e' cx='50' cy='300' r='50'/%3E%3Cg fill='%23008f2d' %3E%3Ccircle cx='0' cy='350' r='50'/%3E%3Ccircle cx='100' cy='350' r='50'/%3E%3C/g%3E%3Ccircle fill='%2300842c' cx='50' cy='400' r='50'/%3E%3Cg fill='%2300792a' %3E%3Ccircle cx='0' cy='450' r='50'/%3E%3Ccircle cx='100' cy='450' r='50'/%3E%3C/g%3E%3Ccircle fill='%23006e29' cx='50' cy='500' r='50'/%3E%3Cg fill='%23006327' %3E%3Ccircle cx='0' cy='550' r='50'/%3E%3Ccircle cx='100' cy='550' r='50'/%3E%3C/g%3E%3Ccircle fill='%23045824' cx='50' cy='600' r='50'/%3E%3Cg fill='%23084e22' %3E%3Ccircle cx='0' cy='650' r='50'/%3E%3Ccircle cx='100' cy='650' r='50'/%3E%3C/g%3E%3Ccircle fill='%230a441f' cx='50' cy='700' r='50'/%3E%3Cg fill='%230c3a1c' %3E%3Ccircle cx='0' cy='750' r='50'/%3E%3Ccircle cx='100' cy='750' r='50'/%3E%3C/g%3E%3Ccircle fill='%230d3019' cx='50' cy='800' r='50'/%3E%3Cg fill='%230d2615' %3E%3Ccircle cx='0' cy='850' r='50'/%3E%3Ccircle cx='100' cy='850' r='50'/%3E%3C/g%3E%3Ccircle fill='%230c1d11' cx='50' cy='900' r='50'/%3E%3Cg fill='%2307140b' %3E%3Ccircle cx='0' cy='950' r='50'/%3E%3Ccircle cx='100' cy='950' r='50'/%3E%3C/g%3E%3Ccircle fill='%23020603' cx='50' cy='1000' r='50'/%3E%3C/g%3E%3C/svg%3E");
background-attachment: fixed;
background-size: contain;

}

.banner-text {
  font-size: 30pt;
  color: cornsilk;

}


</style>


<Container fluid class="container-keywords">
  <Row class="text-center" > 
    <div class="banner text-dark"> 
      <div class="vertical-center banner-text"> Spotify </div> 
    </div> 
  </Row>
</Container>
