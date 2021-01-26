<script>
  import { Container, Row } from 'sveltestrap';

</script>


<style>

  .vertical-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .banner {
    overflow: hidden;
    border-radius: 10px;
    width: 100%;
    height: 210px;
    background-color: #905a00;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1600 800'%3E%3Cg stroke='%23000' stroke-width='66.7' stroke-opacity='0.5' %3E%3Ccircle fill='%23905a00' cx='0' cy='0' r='1800'/%3E%3Ccircle fill='%238f5107' cx='0' cy='0' r='1700'/%3E%3Ccircle fill='%238d480f' cx='0' cy='0' r='1600'/%3E%3Ccircle fill='%238b4014' cx='0' cy='0' r='1500'/%3E%3Ccircle fill='%23873719' cx='0' cy='0' r='1400'/%3E%3Ccircle fill='%23822f1d' cx='0' cy='0' r='1300'/%3E%3Ccircle fill='%237d2821' cx='0' cy='0' r='1200'/%3E%3Ccircle fill='%23772124' cx='0' cy='0' r='1100'/%3E%3Ccircle fill='%23701a26' cx='0' cy='0' r='1000'/%3E%3Ccircle fill='%23691429' cx='0' cy='0' r='900'/%3E%3Ccircle fill='%23600f2a' cx='0' cy='0' r='800'/%3E%3Ccircle fill='%23580b2b' cx='0' cy='0' r='700'/%3E%3Ccircle fill='%234f082b' cx='0' cy='0' r='600'/%3E%3Ccircle fill='%2346062b' cx='0' cy='0' r='500'/%3E%3Ccircle fill='%233c062a' cx='0' cy='0' r='400'/%3E%3Ccircle fill='%23330529' cx='0' cy='0' r='300'/%3E%3Ccircle fill='%23290427' cx='0' cy='0' r='200'/%3E%3Ccircle fill='%23210024' cx='0' cy='0' r='100'/%3E%3C/g%3E%3C/svg%3E");
background-attachment: fixed;
background-size: cover;



  }

</style>


<Container fluid class="container-keywords">
  <Row class="text-center" > 
    <div class="vertical-center banner"> 
      <slot></slot>
    </div> 
  </Row>
</Container>
