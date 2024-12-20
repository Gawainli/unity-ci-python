using System;
using UnityEditor;
using YooAsset.Editor;

public partial class BuildCommand
{
    private const string BuildOutputRoot = "BUILD_OUTPUT_ROOT";
    private const string BuildPipe = "BUILD_PIPE";
    private const string Compression = "COMPRESSION";
    private const string FileNameStyle = "FILE_NAME_STYLE";
    private const string BuildPkgVersion = "BUILD_PKG_VERSION";

    static void PerformBuildYooBundles()
    {
        var buildTarget = GetBuildTarget();
        Console.WriteLine(":: Performing build for YooBundles...");

        var outputPath = GetOutputPath();
        var streamingAssetsPath = AssetBundleBuilderHelper.GetStreamingAssetsRoot();
        TryGetEnv(BuildPipe, out var buildPipeStr);
        var buildPipe = string.IsNullOrEmpty(buildPipeStr)
            ? EBuildPipeline.BuiltinBuildPipeline
            : (EBuildPipeline)int.Parse(buildPipeStr);

        var pkgName = GetPackageName();
        if (string.IsNullOrEmpty(pkgName))
        {
            Console.WriteLine(":: Package name is required.");
            return;
        }

        var pkgVersion = GetPackageVersion();
        var buildMode = GetBuildMode();
        var fileNameStyle = GetFileNameStyle();
        var fileCopyOption = GetBuiltinFileCopyOption();
        var compressOption = GetCompressOption();
        BuildResult result;

        switch (buildPipe)
        {
            case EBuildPipeline.BuiltinBuildPipeline:
                result = PerformBuildYooBundlesBuiltin(buildTarget, outputPath, streamingAssetsPath, pkgName,
                    pkgVersion,
                    buildMode, fileNameStyle, fileCopyOption, compressOption);
                break;
            case EBuildPipeline.ScriptableBuildPipeline:
                result = PerformBuildYooBundlesScriptable(buildTarget, outputPath, streamingAssetsPath, pkgName,
                    pkgVersion,
                    buildMode, fileNameStyle, fileCopyOption, compressOption);
                break;
            case EBuildPipeline.RawFileBuildPipeline:
                result = PerformBuildYooBundlesRawFile(buildTarget, outputPath, streamingAssetsPath, pkgName,
                    pkgVersion,
                    buildMode, fileNameStyle, fileCopyOption);
                break;
            default:
                throw new Exception($"Unsupported build pipe: {buildPipe}");
        }

        if (!result.Success)
        {
            throw new Exception($"Build bundles failed. task:{result.FailedTask}, error:{result.ErrorInfo}");
        }

        Console.WriteLine($":: Package {pkgName} build success.");
    }

    private static string GetOutputPath()
    {
        var outputPath = GetArgument("customBuildPath");
        outputPath = string.IsNullOrEmpty(outputPath)
            ? AssetBundleBuilderHelper.GetDefaultBuildOutputRoot()
            : outputPath;
        if (!outputPath.EndsWith("/"))
        {
            outputPath += "/";
        }

        return outputPath;
    }

    private static ECompressOption GetCompressOption()
    {
        TryGetEnv(Compression, out var compressionStr);
        return string.IsNullOrEmpty(compressionStr)
            ? ECompressOption.LZ4
            : (ECompressOption)int.Parse(compressionStr);
    }

    private static EBuildinFileCopyOption GetBuiltinFileCopyOption()
    {
        var copyOptionStr = GetArgument("copyOption");
        return string.IsNullOrEmpty(copyOptionStr)
            ? EBuildinFileCopyOption.None
            : (EBuildinFileCopyOption)int.Parse(copyOptionStr);
    }

    private static EFileNameStyle GetFileNameStyle()
    {
        TryGetEnv(FileNameStyle, out var fileNameStyleStr);
        return string.IsNullOrEmpty(fileNameStyleStr)
            ? EFileNameStyle.HashName
            : (EFileNameStyle)int.Parse(fileNameStyleStr);
    }

    private static EBuildMode GetBuildMode()
    {
        var buildModeStr = GetArgument("buildMode");
        return string.IsNullOrEmpty(buildModeStr)
            ? EBuildMode.SimulateBuild
            : (EBuildMode)int.Parse(buildModeStr);
    }

    private static string GetPackageVersion()
    {
        // TryGetEnv(BuildPkgVersion, out var pkgVersion);
        var pkgVersion = GetArgument("pkgVersion");
        if (string.IsNullOrEmpty(pkgVersion))
        {
            var now = DateTime.Now;
            var strNow = now.ToString("yyyy-MM-dd-HHmmss");
            pkgVersion = strNow;
        }

        return pkgVersion;
    }

    private static string GetPackageName()
    {
        return GetArgument("pkgName");
    }

    private static BuildResult PerformBuildYooBundlesRawFile(BuildTarget buildTarget, string outputPath,
        string streamingAssetsPath, string pkgName, string pkgVersion, EBuildMode buildMode,
        EFileNameStyle fileNameStyle, EBuildinFileCopyOption fileCopyOption)
    {
        var parameters = new RawFileBuildParameters()
        {
            BuildTarget = buildTarget,
            BuildOutputRoot = outputPath,
            BuildinFileRoot = streamingAssetsPath,
            BuildPipeline = EBuildPipeline.RawFileBuildPipeline.ToString(),
            BuildMode = buildMode,
            PackageName = pkgName,
            PackageVersion = pkgVersion,
            FileNameStyle = fileNameStyle,
            BuildinFileCopyOption = fileCopyOption
        };
        var pipeline = new RawFileBuildPipeline();
        return pipeline.Run(parameters, true);
    }

    private static BuildResult PerformBuildYooBundlesScriptable(BuildTarget buildTarget, string outputPath,
        string streamingAssetsPath, string pkgName, string pkgVersion, EBuildMode buildMode,
        EFileNameStyle fileNameStyle, EBuildinFileCopyOption fileCopyOption, ECompressOption compressOption)
    {
        var parameters = new ScriptableBuildParameters
        {
            BuildTarget = buildTarget,
            BuildOutputRoot = outputPath,
            BuildinFileRoot = streamingAssetsPath,
            BuildPipeline = EBuildPipeline.ScriptableBuildPipeline.ToString(),
            BuildMode = buildMode,
            PackageName = pkgName,
            PackageVersion = pkgVersion,
            FileNameStyle = fileNameStyle,
            BuildinFileCopyOption = fileCopyOption,
            CompressOption = compressOption,
        };

        var pipeline = new ScriptableBuildPipeline();
        return pipeline.Run(parameters, true);
    }

    private static BuildResult PerformBuildYooBundlesBuiltin(BuildTarget buildTarget, string outputPath,
        string streamingAssetsPath, string pkgName, string pkgVersion, EBuildMode buildMode,
        EFileNameStyle fileNameStyle, EBuildinFileCopyOption fileCopyOption, ECompressOption compressOption)
    {
        var parameters = new BuiltinBuildParameters()
        {
            BuildTarget = buildTarget,
            BuildOutputRoot = outputPath,
            BuildinFileRoot = streamingAssetsPath,
            BuildPipeline = EBuildPipeline.BuiltinBuildPipeline.ToString(),
            BuildMode = buildMode,
            PackageName = pkgName,
            PackageVersion = pkgVersion,
            FileNameStyle = fileNameStyle,
            BuildinFileCopyOption = fileCopyOption,
            CompressOption = compressOption,
        };

        var pipeline = new BuiltinBuildPipeline();
        return pipeline.Run(parameters, true);
    }
}