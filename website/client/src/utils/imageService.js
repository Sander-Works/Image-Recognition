import http from './http';

const API_UPLOAD_URL = '/images';

export const upload = async (image) => {
  try {
    const data = new FormData();
    data.append('image', image);
    data.append('fileName', image.name);
    return await http.post(`${API_UPLOAD_URL}`, data, {
      headers: { Accept: 'application/json' },
    });
  } catch (err) {
    console.log(err);
    return err.response;
  }
};

export const getImage = async (id) => {
  try {
    return await http.get(`image/${id}`, {
      responseType: 'blob',
    });
    // return await http.get(`${API_DOWNLOAD_URL}/${id}`);
  } catch (err) {
    return err.response;
  }
};
