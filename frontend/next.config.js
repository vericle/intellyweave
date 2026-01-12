const nextConfig = {
  output: "export",
  productionBrowserSourceMaps: false,
  trailingSlash: false,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
   logging: {
    fetches: {
      fullUrl: false,
    },
  },
  experimental: {
    browserDebugInfoInTerminal: false,
  },
  // Turbopack configuration for GLSL files (Next.js 15)
  turbopack: {
    root: __dirname, // Tell Turbopack this is the root
    rules: {
      '*.glsl': {
        loaders: ['raw-loader'],
        as: '*.js',
      },
      '*.vs': {
        loaders: ['raw-loader'],
        as: '*.js',
      },
      '*.fs': {
        loaders: ['raw-loader'],
        as: '*.js',
      },
      '*.vert': {
        loaders: ['raw-loader'],
        as: '*.js',
      },
      '*.frag': {
        loaders: ['raw-loader'],
        as: '*.js',
      },
    },
  },
  webpack: (config, { isServer }) => {
    // Add a rule to handle .glsl files
    config.module.rules.push({
      test: /\.(glsl|vs|fs|vert|frag)$/,
      exclude: /node_modules/,
      use: [
        {
          loader: "raw-loader", // or "asset/source" in newer Webpack versions
        },
        {
          loader: "glslify-loader",
        },
      ],
    });

    // Exclude pdfjs-dist from server-side bundling
    if (isServer) {
      config.externals = config.externals || [];
      config.externals.push({
        'pdfjs-dist': 'pdfjs-dist',
        'canvas': 'canvas',
      });
    }

    // Handle pdfjs-dist worker file
    config.resolve.alias = {
      ...config.resolve.alias,
      canvas: false,
      fs: false,
    };

    return config;
  },
};

module.exports = nextConfig;
