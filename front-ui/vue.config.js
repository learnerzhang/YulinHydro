module.exports = {
  devServer: {
    hot: true,
    host: '0.0.0.0',
    port: 7000,
    proxy: {
      '/xapi': {
        target: 'http://0.0.0.0:5000',
        changeOrigin: true,
        pathRewrite: {'^/xapi': ''}
      },
      '/other-api': {
        target: 'http://localhost:4000',
        changeOrigin: true,
        pathRewrite: {'^/other-api': ''}
      }
    }
  }
}