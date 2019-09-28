import React from 'react';
import './App.css';

import ImageUploader from 'react-images-upload';
import axios from 'axios'
 
class App extends React.Component {
    constructor(props) {
      super(props)

      this.state = {
        result: null,
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

      axios.post("http://localhost:5000/predict", formData, {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': `multipart/form-data; boundary=${formData._boundary}`,
        }
      }).then((res) => {

        this.setState({
          result: new Buffer(res.data, 'binary').toString('base64') || "",
          loading: false
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
        result: null
      })
    }
 
    render() {
      const {result, loading } = this.state

      let content = <ImageUploader
        withIcon={true}
        accept="accept=image/*"
        buttonText='Choose an image'
        onChange={this.onDrop}
        imgExtension={['.jpg']}
        maxFileSize={5242880}
        singleImage={true}
      />
      if(result) {
        content = <div className="App-header">
          <button className="btn" onClick={this.startover}>Start Over</button><br/>
          <img src={"data:image/jpeg;base64," + result} /> 
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
