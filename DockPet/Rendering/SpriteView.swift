import AppKit

/// Renders pixel-art sprite frames with nearest-neighbor scaling.
///
/// Performance-optimized (M10):
/// - Caches CGImage references to eliminate per-draw allocations
/// - Runs animation timer in .common run loop mode to avoid menu-tracking stutters
/// - Nearest-neighbor filtering for zero blur
/// - Per-pixel alpha hit testing for transparent click-through
final class SpriteView: NSView {

    /// The current animation frames to cycle through.
    private(set) var frames: [NSImage] = []

    /// Cached CGImage representations of the animation frames for zero-allocation rendering.
    private var cgFrames: [CGImage] = []

    /// Index of the currently displayed frame.
    private(set) var currentFrameIndex: Int = 0

    /// Whether the sprite is horizontally flipped (facing left).
    var isFacingLeft: Bool = false {
        didSet {
            if oldValue != isFacingLeft {
                needsDisplay = true
            }
        }
    }

    /// Callback invoked when the sprite is clicked.
    var onClicked: (() -> Void)?

    /// Timer for frame animation.
    private var animationTimer: Timer?

    /// Whether the current animation should loop.
    private var animationLoops: Bool = true

    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("Not implemented")
    }

    private func setupLayer() {
        wantsLayer = true
        // Nearest-neighbor filtering for crisp pixel art
        layer?.magnificationFilter = .nearest
        layer?.minificationFilter = .nearest
    }

    // MARK: - Animation Control

    /// Sets the animation frames and starts playback.
    ///
    /// - Parameters:
    ///   - frames: Array of NSImage frames.
    ///   - fps: Frames per second for animation.
    ///   - loop: Whether to loop the animation.
    func setAnimation(frames: [NSImage], fps: Double, loop: Bool = true) {
        stopAnimation()

        self.frames = frames
        self.cgFrames = frames.compactMap { img in
            img.cgImage(forProposedRect: nil, context: nil, hints: nil)
        }
        self.currentFrameIndex = 0
        self.animationLoops = loop

        needsDisplay = true

        guard frames.count > 1, fps > 0 else { return }

        let interval = 1.0 / fps
        let timer = Timer(timeInterval: interval, repeats: true) { [weak self] _ in
            self?.advanceFrame()
        }
        RunLoop.main.add(timer, forMode: .common)
        self.animationTimer = timer
    }

    /// Stops the current animation.
    func stopAnimation() {
        animationTimer?.invalidate()
        animationTimer = nil
    }

    private func advanceFrame() {
        guard !cgFrames.isEmpty else { return }

        let nextIndex = currentFrameIndex + 1

        if nextIndex >= cgFrames.count {
            if animationLoops {
                currentFrameIndex = 0
            } else {
                stopAnimation()
                return
            }
        } else {
            currentFrameIndex = nextIndex
        }

        needsDisplay = true
    }

    // MARK: - Drawing

    override func draw(_ dirtyRect: NSRect) {
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }
        guard currentFrameIndex < cgFrames.count else {
            ctx.clear(bounds)
            return
        }

        ctx.clear(bounds)
        ctx.interpolationQuality = .none

        let cgImage = cgFrames[currentFrameIndex]

        ctx.saveGState()

        if isFacingLeft {
            // Flip horizontally: translate to right edge, scale X by -1
            ctx.translateBy(x: bounds.width, y: 0)
            ctx.scaleBy(x: -1, y: 1)
        }

        ctx.draw(cgImage, in: bounds)
        ctx.restoreGState()
    }

    // MARK: - Click Handling

    override func mouseDown(with event: NSEvent) {
        let locationInView = convert(event.locationInWindow, from: nil)
        if isOpaquePixel(at: locationInView) {
            onClicked?()
        }
    }

    override func hitTest(_ point: NSPoint) -> NSView? {
        let localPoint = convert(point, from: superview)
        guard bounds.contains(localPoint) else { return nil }

        if isOpaquePixel(at: localPoint) {
            return self
        }
        return nil
    }

    // MARK: - Pixel Hit Testing

    private func isOpaquePixel(at point: NSPoint) -> Bool {
        guard currentFrameIndex < cgFrames.count else { return false }

        let cgImage = cgFrames[currentFrameIndex]
        let imageWidth = cgImage.width
        let imageHeight = cgImage.height

        var pixelX = Int(point.x / bounds.width * CGFloat(imageWidth))
        let pixelY = imageHeight - 1 - Int(point.y / bounds.height * CGFloat(imageHeight))

        if isFacingLeft {
            pixelX = imageWidth - 1 - pixelX
        }

        guard pixelX >= 0, pixelX < imageWidth, pixelY >= 0, pixelY < imageHeight else { return false }

        guard let dataProvider = cgImage.dataProvider,
              let data = dataProvider.data,
              let ptr = CFDataGetBytePtr(data) else { return false }

        let bytesPerPixel = cgImage.bitsPerPixel / 8
        let bytesPerRow = cgImage.bytesPerRow
        let offset = pixelY * bytesPerRow + pixelX * bytesPerPixel

        let alphaIndex = bytesPerPixel - 1
        let alpha = ptr[offset + alphaIndex]

        return alpha > 20
    }

    deinit {
        stopAnimation()
    }
}
