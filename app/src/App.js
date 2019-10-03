import React from 'react';
import './App.css';

import ImageUploader from 'react-images-upload';
import axios from 'axios'
 
class App extends React.Component {
    constructor(props) {
      super(props)

      this.state = {
        result: null,
        angle: null,
        vertebras: null,
        loading: false
      }
    }

    onDrop = (pictures) => {
      this.setState({
        loading: true
      })
      let picture = pictures[0]
      
      let formData = new FormData()
      formData.append('image', picture, picture.fileName)

      axios.post("http://localhost:5000/get_image", formData, {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': `multipart/form-data; boundary=${formData._boundary}`,
        }
      }).then((res) => {

        axios.get("http://localhost:5000/get_angle").then(({data }) => {
          this.setState({
            result: new Buffer(res.data, 'binary').toString('base64') || "",
            angle: data.angle,
            vertebras: data.vertebras,
            loading: false
          })
        })
      }).catch((err) => {
        console.log(err)
        this.setState({
          loading:false
        })
      })
    }

    startover = () => {
      this.setState({
        result: null,
        angle: null,
        vertebras: null,
        loading: false
      })
    }
 
    render() {
      const {result, vertebras, angle, loading } = this.state

      let content = <ImageUploader
        withIcon={true}
        accept="accept=image/*"
        buttonText='Choose an image'
        onChange={this.onDrop}
        imgExtension={['.jpg']}
        maxFileSize={5242880}
        singleImage={true}
      />
      if(result && angle) {
        content = <div className="App-header">
          <button className="btn" onClick={this.startover}>Start Over</button><br/>
          <img src={"data:image/jpeg;base64," + result} /> 
          <p></p>
          <div>
            Most tilt vertebras are: {vertebras}, Cobb angle is: {angle}
            <br />
          </div>
        </div>
        
      } 

      if(loading) {
        content = <div style={{textAlign: 'center'}}>
          <div className="loader" />
        </div>
      }

      return (
        <div className="App">
          <h3>Cobb Angle Calculator</h3>  
          {content}
        </div>
      ); 
    }
}

export default App;
