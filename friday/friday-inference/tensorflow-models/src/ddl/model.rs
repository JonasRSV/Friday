use tensorflow_rust_sys;
use std::path::Path;
use std::ffi::CString;
use libc;

use friday_logging;

#[cfg(target_arch="x86_64")] pub type Char = i8;
#[cfg(target_arch="x86_64")] pub type UInt = u64;

#[cfg(target_arch="arm")] pub type Char = u8;
#[cfg(target_arch="arm")] pub type UInt = u32;


pub trait TensorDataTypes: Sized {
    fn size(&self) -> usize;
    fn copy(from : &Vec<Self>, target: *mut libc::c_void);

}

impl TensorDataTypes for i16 {

    fn size(&self) -> usize {
        return std::mem::size_of::<i16>();
    }

    fn copy(from : &Vec<Self>, target: *mut libc::c_void) {
        let data_sz =  std::mem::size_of::<i16>() * from.len();


        unsafe { libc::memcpy(target, from.as_ptr() as *const libc::c_void, data_sz) };
    }
}

impl TensorDataTypes for Vec<f32> {
    fn size(&self) -> usize {
        return std::mem::size_of::<f32>() * self.len();
    }

    fn copy(from : &Vec<Self>, target: *mut libc::c_void) {
        let mut offset = 0;
        for vec in from.iter() {
            let data_sz = std::mem::size_of::<f32>() * vec.len();

            unsafe { libc::memcpy(target.offset(offset), vec.as_ptr() as *const libc::c_void, data_sz) };

            offset += data_sz as isize;
        }
    }
}

fn is_status_ok(status: *const tensorflow_rust_sys::TF_Status) -> bool {
    unsafe {
        if tensorflow_rust_sys::TF_GetCode(status) != tensorflow_rust_sys::TF_Code_TF_OK {
            let message = CString::from_raw(tensorflow_rust_sys::TF_Message(status) as *mut Char);
            let rust_message = message.to_str().expect("Failed to make string");

            friday_logging::fatal!("(tensorflow-models): Error {}", rust_message);

            return false;
        }

        return true;
    }
}

#[derive(Clone)]
pub struct Tensor {
    tensor: *mut tensorflow_rust_sys::TF_Tensor,
    op: tensorflow_rust_sys::TF_Output,

    pub dims: Vec<i64>,

    data_type: tensorflow_rust_sys::TF_DataType,
    data: *mut libc::c_void,

    is_empty: bool,
    is_valid: bool

}

impl Tensor {
    pub fn new(model: &Model, op_name: &CString) -> Tensor {
        friday_logging::info!("Loading tensor {}", op_name.to_str().expect("Failed to convert op_name to string"));
        let op = tensorflow_rust_sys::TF_Output {
            oper: unsafe { tensorflow_rust_sys::TF_GraphOperationByName(model.graph, op_name.as_ptr()) },
            index:  0
        };

        if op.oper.is_null() {
            panic!("(tensorflow-models): No operation named {}", 
                op_name.to_str().expect("Failed to convert op_name to string"));
        }


        // Get number of dimensions
        let n_dims = unsafe { tensorflow_rust_sys::TF_GraphGetTensorNumDims(model.graph, op, model.status) };
        if !is_status_ok(model.status) {
            panic!("(tensorflow-models): Failed to get dims of op {}", op_name.to_str().expect("Failed to convert op_name to string"))
        }

        let data_type = unsafe { tensorflow_rust_sys::TF_OperationOutputType(op) };

        let mut dims: Vec<i64> = Vec::new();
        let c_dims = unsafe {libc::malloc(std::mem::size_of::<i64>() * n_dims as usize) as *mut i64};

        unsafe { tensorflow_rust_sys::TF_GraphGetTensorShape(model.graph, op, c_dims, n_dims, model.status) };

        if ! is_status_ok(model.status) {
            panic!("(tensorflow-models): Failed to get shape of tensor for op {}", 
                op_name.to_str().expect("Failed to convert op_name to string"))
        }

        for i in 0..n_dims {
            dims.push(unsafe { *c_dims.add(i as usize)  });
        }

        friday_logging::info!("Successfully loaded tensor {:?}", op_name);
        return Tensor{
            tensor: std::ptr::null::<tensorflow_rust_sys::TF_Tensor>() as *mut tensorflow_rust_sys::TF_Tensor,
            op,
            dims,
            data_type,
            data: std::ptr::null::<libc::c_void>() as *mut libc::c_void,
            is_empty: true,
            is_valid: true

        };
    }

    pub fn set_data<T: TensorDataTypes> (&mut self, data: &Vec<T>) {
        if !self.is_empty {
            unsafe {tensorflow_rust_sys::TF_DeleteTensor(self.tensor) };
            self.is_empty = true
        }

        if !self.is_valid {
            panic!("(tensorflow-models): Trying to set data on an invalid tensor");
        }


        let data_sz = data.first().expect("cannot set empty data").size() * data.len();
        let c_data = unsafe {libc::malloc(data_sz)};

        T::copy(data, c_data);

        unsafe extern "C" fn deallocator(
            data: *mut libc::c_void,
            _: tensorflow_rust_sys::size_t,
            _: *mut libc::c_void,
        ) {
            libc::free(data);
        }

        self.tensor = unsafe {
            tensorflow_rust_sys::TF_NewTensor(
                /*TF_DataType=*/self.data_type, 
                /*dims=*/self.dims.as_ptr(), 
                /*num_dims=*/self.dims.len() as i32, 
                /*data=*/c_data, 
                /*length=*/data_sz as UInt,
                /*deallocator=*/Some(deallocator),
                /*deallocator_args=*/std::ptr::null::<libc::c_void>() as *mut libc::c_void)
        };

        if self.tensor.is_null() {
            panic!("(tensorflow-models): Failed to allocate new tensor when setting data");
        }

        self.is_empty = false;
    }

    pub fn get_data<T>(&mut self) -> Vec<T> 
        where T: Clone {
            if self.is_empty {
                panic!("(tensorflow-models): Trying to get data from empty tensor");
            }

            if !self.is_valid {
                panic!("(tensorflow-models): Trying to get data from an invalid tensor");
            }

            let data = unsafe {
                tensorflow_rust_sys::TF_TensorData(self.tensor)
            };

            if data.is_null() {
                panic!("(tensorflow-models): Tensor data is empty");
            }

            let data_size = self.dims.first().expect("(tensorflow-models): Failed to unwrap dims").clone() as usize;
            return unsafe { std::slice::from_raw_parts(data as *const T, data_size).to_vec()};
        }

    fn free_tensor(&mut self) {
        if !self.is_empty {
            unsafe {tensorflow_rust_sys::TF_DeleteTensor(self.tensor) };
        }
        self.is_empty = true;
        self.data = std::ptr::null::<libc::c_void>() as *mut libc::c_void;
    }

}

#[derive(Clone)]
pub struct Model {
    graph: *mut tensorflow_rust_sys::TF_Graph,
    session: *mut tensorflow_rust_sys::TF_Session,
    status: *mut tensorflow_rust_sys::TF_Status
}

impl Model {

    pub fn free_tensorflow_resources(&mut self) -> bool {
        unsafe {
            tensorflow_rust_sys::TF_DeleteGraph(self.graph);
            tensorflow_rust_sys::TF_DeleteSession(self.session, self.status);

            if is_status_ok(self.status) {
                tensorflow_rust_sys::TF_DeleteStatus(self.status);

                return true;
            }
            return false;
        };

    }

    pub fn new(export_dir: &Path) -> Option<Model> {
        friday_logging::info!("(tensorflow-models): Loading {}", 
            export_dir.to_str().expect("Failed to convert path to String"));
        let status = unsafe { tensorflow_rust_sys::TF_NewStatus() };
        let graph = unsafe { tensorflow_rust_sys::TF_NewGraph() };
        let session_options = unsafe { tensorflow_rust_sys::TF_NewSessionOptions() };

        // This is a encoded proto that tells tensorflow to only use one thread in inference (to
        // save resources)
        let magic_string = CString::new("\x10\x01(\x01").expect("Failed to create magic str");
        let magic_void : *mut libc::c_void = magic_string.as_ptr() as *mut libc::c_void;


        unsafe {tensorflow_rust_sys::TF_SetConfig(
            /*options=*/session_options, 
            /*proto=*/magic_void, 
            /*proto_len=*/4, 
            /*status=*/status) 
        };

        if ! is_status_ok(status) {
            return None;
        }


        let null_ptr: *mut tensorflow_rust_sys::TF_Buffer = 
            std::ptr::null::<tensorflow_rust_sys::TF_Buffer>() as *mut tensorflow_rust_sys::TF_Buffer;


        let export_dir: CString = CString::new(export_dir.to_str()
            .expect("Failed to convert path to String"))
            .expect("Failed to create CString");

        let tags = CString::new("serve").expect("Failed to create CString");

        let session = unsafe { tensorflow_rust_sys::TF_LoadSessionFromSavedModel(
            /*session_options=*/session_options,
            /*run_options=*/null_ptr,
            /*export_dir=*/export_dir.as_ptr(),
            /*tags=*/&tags.as_ptr(),
            /*ntags=*/1,
            /*graph=*/graph, 
            null_ptr,
            /*status=*/status)
        };

        // Can delete sess opts here already since we wont use em
        unsafe { tensorflow_rust_sys::TF_DeleteSessionOptions(session_options) };

        if is_status_ok(status) {
            friday_logging::info!("(tensorflow-models): Successfully loaded session from saved model");
            return Some(Model {
                graph,
                session,
                status
            });
        }

        return None
    }

    pub fn run_projection(&mut self, input: &mut Tensor, output: &mut Tensor) {
        if input.is_empty {
            panic!("(tensorflow-models): Trying to run with empty input tensor");
        }

        if !output.is_valid {
            panic!("(tensorflow-models): Trying to run with invalid output tensor");
        }


        let null_ptr: *mut tensorflow_rust_sys::TF_Buffer = 
            std::ptr::null::<tensorflow_rust_sys::TF_Buffer>() as *mut tensorflow_rust_sys::TF_Buffer;

        // Clear output
        output.free_tensor();


        unsafe {
            tensorflow_rust_sys::TF_SessionRun(
                /*session=*/self.session,
                /*run_opts=*/null_ptr,
                /*input_ops=*/&input.op,
                /*input_values=*/&input.tensor,
                /*num_inputs=*/1,
                /*output_ops=*/&output.op,
                /*output_values=*/&mut output.tensor,
                /*num_outputs=*/1,
                /*target_operations=*/&(null_ptr as *const tensorflow_rust_sys::TF_Operation),
                /*num_targets=*/0,
                /*run_metadata=*/null_ptr,
                /*status=*/self.status)
        };

        if is_status_ok(self.status) {
            output.is_empty = false;
            input.free_tensor();
        } else {
            panic!("(tensorflow-models): Failed to execute tensorflow session");
        }
    }

    pub fn run_distances(&mut self, 
        audio_input: &mut Tensor, 
        embeddings_input: &mut Tensor, 
        output: &mut Tensor) {

        if audio_input.is_empty {
            panic!("(tensorflow-models): Trying to run with empty audio input tensor");
        }

        if embeddings_input.is_empty {
            panic!("(tensorflow-models): Trying to run with empty embeddings input tensor");
        }

        if !output.is_valid {
            panic!("(tensorflow-models): Trying to run with invalid output tensor");
        }


        let null_ptr: *mut tensorflow_rust_sys::TF_Buffer = 
            std::ptr::null::<tensorflow_rust_sys::TF_Buffer>() as *mut tensorflow_rust_sys::TF_Buffer;

        // Clear output
        output.free_tensor();

        let input_ops = vec![audio_input.op, embeddings_input.op];
        let input_values = vec![audio_input.tensor, embeddings_input.tensor];


        unsafe {
            tensorflow_rust_sys::TF_SessionRun(
                /*session=*/self.session,
                /*run_opts=*/null_ptr,
                /*input_ops=*/input_ops.as_ptr(),
                /*input_values=*/input_values.as_ptr(),
                /*num_inputs=*/2,
                /*output_ops=*/&output.op,
                /*output_values=*/&mut output.tensor,
                /*num_outputs=*/1,
                /*target_operations=*/&(null_ptr as *const tensorflow_rust_sys::TF_Operation),
                /*num_targets=*/0,
                /*run_metadata=*/null_ptr,
                /*status=*/self.status)
        };

        if is_status_ok(self.status) {
            output.is_empty = false;
            audio_input.free_tensor();
            embeddings_input.free_tensor();
        } else {
            panic!("(tensorflow-models): Failed to execute tensorflow session");
        }
    }

}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_ddl_load_model_and_tensors() {
        let model_path = Path::new("test-resources/ddl_apr_13_eu");
        let mut model = Model::new(&model_path).expect("Failed to create model");

        let input_audio_op_name = CString::new("audio").expect("Failed to create input name");
        let input_embeddings_op_name = CString::new("embeddings").expect("Failed to create input name");

        let output_project_op_name = CString::new("project").expect("Failed to create input name");
        let output_distance_op_name = CString::new("distances").expect("Failed to create input name");


        let mut input_audio_tensor = Tensor::new(&model, &input_audio_op_name);
        let mut input_embeddings_tensor = Tensor::new(&model, &input_embeddings_op_name);

        let mut output_project_tensor = Tensor::new(&model, &output_project_op_name);
        let mut output_distance_tensor = Tensor::new(&model, &output_distance_op_name);

        let v1: Vec<i16> = vec![1; 16000];

        friday_logging::info!("Audio tensor size {}", v1.len());
        friday_logging::info!("audio datatype {}", input_audio_tensor.data_type);

        input_audio_tensor.set_data(&v1);
        let u: Vec<i16> = input_audio_tensor.get_data();
        assert_eq!(v1, u);

        let mut project_input: Vec<&mut Tensor> = Vec::new();
        project_input.push(&mut input_audio_tensor);

        model.run_projection(&mut input_audio_tensor, &mut output_project_tensor);

        let v1_projection = output_project_tensor.get_data::<f32>();
        friday_logging::info!("output datatype: {}", output_project_tensor.data_type);
        friday_logging::info!("{:?}", v1_projection);


        friday_logging::info!("Freeing went fine Woo!");

        let v2: Vec<i16> = vec![0; 16000];
        input_audio_tensor.set_data(&v2);
        model.run_projection(&mut input_audio_tensor, &mut output_project_tensor);
        let v2_projection = output_project_tensor.get_data::<f32>();

        let embeddings = vec![v1_projection, v2_projection];

        //Run distance op
        input_audio_tensor.set_data(&v2);
        friday_logging::info!("Setting went fine!");

        // Need to set unknown dimensions
        input_embeddings_tensor.dims[0] = 2;
        output_distance_tensor.dims[0] = 2;

        friday_logging::info!("embedding datatype {}", input_embeddings_tensor.data_type);
        friday_logging::info!("audio shape {:?}", input_audio_tensor.dims);
        friday_logging::info!("embedding shape {:?}", input_embeddings_tensor.dims);
        friday_logging::info!("distance shape {:?}", output_distance_tensor.dims);
        input_embeddings_tensor.set_data(&embeddings);
        friday_logging::info!("Setting went fine!");
        input_embeddings_tensor.dims[0] = -1;
        model.run_distances(&mut input_audio_tensor, &mut input_embeddings_tensor, &mut output_distance_tensor);
        friday_logging::info!("{:?}", output_distance_tensor.get_data::<f32>());
        friday_logging::info!("Loading went fine!");
        model.free_tensorflow_resources();

    }
}
